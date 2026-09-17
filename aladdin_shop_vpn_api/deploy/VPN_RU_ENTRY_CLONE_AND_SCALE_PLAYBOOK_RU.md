# AiMonkey VPN — ГЛАВНЫЙ файл (канон)

**Это единственный главный ops-файл по VPN.**  
Для владельца и любой ML/агент-системы. Секреты (ключи, токены) сюда **не** пишем.

---

## SSOT 2026-09-17 — флот · роли · OPS (для другой ML)

**Ничего ниже по файлу не удаляли** — этот блок **добавлен в начало**, чтобы любая ML сразу видела актуальную картину.

**Hetzner у нас нет.** Провайдеры: Contabo · FirstVDS · REG.RU · Яндекс.Облако.  
Слово «хостинг» не используем. Именование в ответах: `.cursor/rules/vpn-server-naming-speak.mdc`.

### Сколько серверов

| | |
|---|---|
| **Всего машин** | **7** |
| Contabo | **3** — Brain, Mouth, SG |
| FirstVDS | **2** — NEW (мост), MAIN (Аладдин) |
| REG.RU | **1** — REG |
| Яндекс.Облако | **1** — Обход-ночь (NLB + ВМ) |
| Без Аладдина (MAIN) | **6** |

**Стоимость флота (ориентир, без детализации счёта Аладдина в OPS-строке):** Contabo 1 200×3 + FirstVDS NEW 1 600 + REG.RU 1 600 + Яндекс 3 000 ≈ **9 800 ₽** → в OPS пишем **`💰 Серверы ≈ 10 000 ₽/мес`**.

### Кратко по каждому (одна фраза)

| Сервер | Одной фразой |
|--------|----------------|
| 🇩🇪 **Brain** Contabo `…150` | **мозг** — тут бот, vpn-api, OPS, касса |
| 🇫🇷 **Mouth** Contabo `…12` | **рот** — бот говорит с Telegram (отдельный сервер от мозга) |
| 🇸🇬 **SG** Contabo `…78` | **двор** — выход Asia |
| 🇷🇺 **NEW** FirstVDS `…98` | **мост** — вход VPN (день; профили EU / Asia / lab) |
| 🇷🇺 **MAIN** FirstVDS `…180` | **Аладдин · запас** — приложение iOS API + запасная (warm) дверь |
| 🇷🇺 **REG** REG.RU `…63` | **ночь** — ночная дверь `:443` / `:8443` (не пустой; hop → NEW) |
| 🇷🇺 **Яндекс** NLB `…20` · ВМ `158.x` | **Обход-ночь** — LTE-дверь (staging/канон ночи) |

### Как устроено (день / Азия / ночь)

```
День EU:   телефон → NEW:8444 → WG → Brain egress
День Asia: телефон → NEW:8445 → hop → SG egress
Ночь LTE:  телефон → Яндекс NLB:443 (и/или REG:443|:8443 → NEW) → …
Бот TG:    Brain → Mouth → Telegram
```

### AiMonkey OPS (отчёт админам 3×/день)

| | |
|---|---|
| Заголовок | `🛡 AiMonkey OPS` (не ALADDIN) |
| Слоты МСК | **09:00 / 14:00 / 21:00** · timer на Brain `aladdin-vpn-ops-command-center.timer` |
| Скрипт | `/opt/aladdin-shop-vpn-api/deploy/scripts/vpn_ops_command_center.py` · репо: `aladdin_shop_vpn_api/deploy/scripts/` |
| Docs | `aladdin_shop_vpn_api/deploy/VPN_OPS_COMMAND_CENTER_RU.md` |

**🚪 Двери** — живы ли входы (медиана из **3** TCP-проб, одна цифра ms):  
Contabo: Brain + Mouth · FirstVDS: NEW×3 порта + MAIN запас · REG.RU ночь×2 · Яндекс ночь.  
Повторов **машин** нет: у NEW/REG несколько **портов** одного сервера.

**🔗 Мост WG** — связь серверов между собой (**не** скорость): NEW, MAIN, REG, SG двор, Яндекс.

**🛡 Guard** — в отчёте только **платные + триал** (без ссылок друзьям TID `9901*`, без tid≤0).  
**⚡ Скорость** — tunnel/path MB/s. **🧩 Сервисы** — bot / vpn-api / partner на Brain + MAIN API.

### Speed / §32 secrets

`VPN_SPEED_DEGRADATION_HANDOFF_RU.md` — **только ссылка** в карте ниже; **не** склеивать в этот playbook и **не** пушить секреты.

### Зеркало

Тот же канон: `~/ALADDIN_VPN_SAFE/ENTRY_CLONE_KIT/README.md`. SSH/IP: канон #3 `SERVERS_ACCESS_CANON.md` (сейф).

---

| | |
|---|---|
| **Дата канона** | 2026-08-05 · … · **P01 NLB ночь LTE PASS:** **2026-09-12 ~04:47** · SSOT `ML_SYSTEM_HANDOFF_P01_YANDEX_NIGHT_DOOR_2026-09-11.md` **§23** · **флот/OPS SSOT:** **2026-09-17** (блок выше) |
| **Сейф Mac** | `~/ALADDIN_VPN_SAFE/` (+ зеркало **этого** файла: `ENTRY_CLONE_KIT/README.md`) |
| **Правило окон** | Не мешать в один день: cutover entry + Lava + routing + смена egress |

### Три канона — с чего начать ML

| # | Задача | Открыть | В git? |
|---|--------|---------|--------|
| **1** | Ops VPN + **архитектура §0.3** + бот/Lava/cutover + карта всех MD | **← этот файл** · сейф: `ENTRY_CLONE_KIT/README.md` | ✅ / зеркало |
| **2** | Глушилки Dendi + план `jam-*` · companion three-way (Frosty/rollout) | `VPN_JAMMING_DENDI_VS_AIMONKEY_ANALYSIS_AND_PLAN_2026-08-20.md` · + `VPN_JAMMING_THREE_WAY_DENDI_FROSTY_AIMONKEY_2026-08-26.md` | ✅ |
| **3** | SSH, IP, алиасы, пароли, роли серверов (в т.ч. REG.RU) | `~/ALADDIN_VPN_SAFE/ENTRY_CLONE_KIT/SERVERS_ACCESS_CANON.md` | ❌ сейф |

**Ночь LTE / обход глушилок — с чего начать ML (12.09):**  
`ML_SYSTEM_HANDOFF_JAMMING_BYPASS_INDEX_AND_CHECKLIST_2026-09-12.md` (карта + чеклист) →  
`ML_SYSTEM_HANDOFF_P01_NLB_VS_BARE_IP_JAMMING_2026-09-12.md` (почему голый IP умер) →  
P01 **§23**. Этот файл = день/Азия/мозг/касса. Сейф: `ENTRY_CLONE_KIT/README.md`.

**Хватит ли другой ML?** Да, если есть **репо `ALADDIN_iOS`** + **сейф на Mac** + ключ **`~/.ssh/aladdin_server`**. Файл **3** без ключа — только справочник, не вход.

**Speed / recovery (§32 secrets):** `VPN_SPEED_DEGRADATION_HANDOFF_RU.md` — **только ссылка** в карте ниже; **не** merge сюда и **не** в канон #3.

### Что лучше сделать заранее (решение владельца 2026-09-12)

| # | Вариант | Статус |
|---|---------|--------|
| **1** | Собрать **золотой набор P01** в `~/ALADDIN_VPN_SAFE/P01_GOLDEN_DOOR_KIT/` (без секретов, без новой ВМ). Следующая ночь глушилок = **часы**, не с нуля. | **✅ СДЕЛАНО 2026-09-12** · README набора |
| **2** | Купить тёплый Timeweb заранее — платите, пока Яндекс ещё жив; смысл только если нужен запас до пожара. | **не делали** · отдельный GO |
| **3** | Ничего не готовить — клон всё равно возможен, но снова вечер ручной работы. | отвергнуто |

Новые сервера и `VPN_SUBSCRIBE_P01_MODE=all` **без явного GO не трогаем**. Клон ночи: P01 **§11.2** + этот набор. Не путать с клоном NEW в **§4**.

### Карта ссылок (все связанные MD) — хаб для ML

#### A. Три канона + архитектура

| Тема | Файл |
|------|------|
| **Обход глушилок — индекс + чеклист (12.09)** | `ML_SYSTEM_HANDOFF_JAMMING_BYPASS_INDEX_AND_CHECKLIST_2026-09-12.md` |
| **Почему голый Яндекс умер / NLB** | `ML_SYSTEM_HANDOFF_P01_NLB_VS_BARE_IP_JAMMING_2026-09-12.md` |
| **← ВЫ ЗДЕСЬ (канон #1)** | `VPN_RU_ENTRY_CLONE_AND_SCALE_PLAYBOOK_RU.md` · **§0.3 архитектура LIVE** · сейф `ENTRY_CLONE_KIT/README.md` |
| Канон #2 Dendi | `VPN_JAMMING_DENDI_VS_AIMONKEY_ANALYSIS_AND_PLAN_2026-08-20.md` |
| Three-way (companion #2) | `VPN_JAMMING_THREE_WAY_DENDI_FROSTY_AIMONKEY_2026-08-26.md` |
| Канон #3 SSH/IP | `~/ALADDIN_VPN_SAFE/ENTRY_CLONE_KIT/SERVERS_ACCESS_CANON.md` |
| Зеркало playbook в сейфе | `~/ALADDIN_VPN_SAFE/ENTRY_CLONE_KIT/README.md` |
| TODO `jam-*`/`fro-*` | `.cursor/VPN_JAMMING_TASK_REGISTRY.md` |
| Чеклист остатка | `REMAINING_CHECKLIST_JAMMING_2026-08-27.md` |
| Cursor rule jamming | `.cursor/rules/vpn-jamming-dendi-todo-ssot.mdc` |
| Именование серверов в ответах | `.cursor/rules/vpn-server-naming-speak.mdc` |

#### B. Data-plane / entry / P9 / глушилки

| Тема | Файл |
|------|------|
| **P9 REG.RU restore (PASS 2026-08-29)** | `ML_SYSTEM_HANDOFF_P9_REG_RU_LTE_NIGHT_2026-08-29.md` · **§5.1 Ideal A ❌** |
| **Cheb vs Dendi vs Frosty vs мы (2026-09-01)** | `ML_SYSTEM_HANDOFF_CHEBURASHKA_VS_DENDI_FROSTY_AIMONKEY_2026-09-01.md` |
| P9 гибрид план | `VPN_P9_HYBRID_BRIDGE_PLAN_2026-08-28.md` |
| P9 форумы/провайдеры | `VPN_P9_FORUM_PROVIDER_RESEARCH_2026-08-28.md` |
| LTE негативные тесты 28.08 | `ML_SYSTEM_HANDOFF_JAMMING_LTE_NEGATIVE_TESTS_2026-08-28.md` · **§18.8** · **§19** |
| Frosty/jamming handoff | `ML_SYSTEM_HANDOFF_VPN_JAMMING_FROSTY_2026-08-27.md` |
| jam-41 xHTTP lab runbook | `runbooks/JAM41_XHTTP_GRPC_LTE_LAB_WITHOUT_NEW_VPS_2026-08-28.md` |
| Миграция entry 0–12 | `VPN_RU_ENTRY_SPLIT_MIGRATION_PLAN_RU.md` |
| Cutover 149→NEW | `CUTOVER_149_TO_NEW_RUNBOOK_RU.md` |
| Split RU direct | `VPN_SPLIT_RU_DIRECT_RUNBOOK_RU.md` |
| P6 ads + casino routing | `VPN_ROUTING_ADS_CASINO_PLAN_2026-08-28.md` |
| Код routing JSON | `aladdin_shop_vpn_api/routing_casino_slots.json` · `routing_ru_direct.json` |
| Resilience minplan | `VPN_RESILIENCE_MINPLAN_RU.md` |
| Failover / reserve egress | `VPN65_BRIDGE_FAILOVER_RUNBOOK.md` · `VPN76_RESERVE_EGRESS_RUNBOOK.md` |
| Path diagnostics | `VPN_PATH_SPEED_DIAGNOSTICS_PLAN_RU.md` |
| **Xray lifecycle без массовых restart (диагноз/fix 2026-09-08)** | `VPN_XRAY_ZERO_DOWNTIME_USER_SYNC_RUNBOOK_2026-09-08.md` · локально готов, **не deployed** |
| **Speed handoff (§32 — не в git/чат)** | `VPN_SPEED_DEGRADATION_HANDOFF_RU.md` — **только ссылка** |
| Stream speed hybrid | **§14** · `telegram_stars_shop_bot/docs/PLAN_VPN_STREAM_SPEED_HYBRID_2026-08-13.md` · `…/ML_SYSTEM_HANDOFF_VPN_STREAM_SPEED_HYBRID_2026-08-14.md` |
| **Ideal-gap + эксперименты LN A/B (2026-09-07)** | `ML_SYSTEM_HANDOFF_VPN_IDEAL_GAP_AND_EXPERIMENTS_2026-09-07.md` · план `…/PLAN_VPN_LTE_NIGHT_RELIABILITY_BEST_PATH_2026-09-05.md` |
| **Ночь LTE + глушилки: REG «не помогает» · конкуренты · next (2026-09-07)** | `ML_SYSTEM_HANDOFF_LTE_NIGHT_JAMMING_REG_COMPETITORS_2026-09-07.md` |
| **P01 Yandex ночь LTE PASS (2026-09-12 ~04:47) — SSOT** | `ML_SYSTEM_HANDOFF_P01_YANDEX_NIGHT_DOOR_2026-09-11.md` **§23** · CDN FAIL **§22** · этот файл **§0.3** + **§19.12** |
| **Золотой набор клона ночи (2026-09-12)** | `~/ALADDIN_VPN_SAFE/P01_GOLDEN_DOOR_KIT/` · **не git** · бинарь + шаблоны без ключей |
| **HTTP-CDN как Mops — FAIL 12.09** | `PLAN_P01_YANDEX_NIGHT_CDN_MOPS_2026-09-12.md` · клики-история `RUNBOOK_P01_YANDEX_CDN_MOPS_CONSOLE_2026-09-12.md` · не `jam-50/51` |
| **NLB сырой :443 — LIVE LTE PASS** | `84.201.151.20` · сравнение `ML_SYSTEM_HANDOFF_P01_NLB_VS_BARE_IP_JAMMING_2026-09-12.md` · клики `RUNBOOK_P01_YANDEX_NLB_PASSTHROUGH_CONSOLE_2026-09-12.md` · выдача = P01 **§23.4** |
| P2 Asia-via-NEW | **§18** · GOLDEN `~/ALADDIN_VPN_SAFE/GOLDEN_P2_ASIA_VIA_NEW_LATEST` |

#### C. Control-plane / бот / касса / клиенты

| Тема | Файл |
|------|------|
| Shop Bot архитектура | `telegram_stars_shop_bot/docs/BOT_ARCHITECTURE_REFERENCE_RU.md` · **§15** |
| Деплой бота | `…/ML_SYSTEM_HANDOFF_FINAL.md` · rule `telegram-shop-bot-deploy-safe.mdc` |
| Bot API soft-block | **§15.8** · `…/ML_SYSTEM_HANDOFF_TELEGRAM_BOTAPI_SOFTBLOCK.md` |
| Бот молчит, getMe жив (display_seq / lock) | **§15.9** · `…/ML_SYSTEM_HANDOFF_BOT_SILENT_DISPLAY_SEQ_LOCK_2026-09-04.md` |
| LAVA СБП/карта | **§17** · `…/ML_SYSTEM_HANDOFF_PAYMENTS_LAVA_H2H_CLASSIC_2026-08-17.md` |
| **LAVA хаб (все планы + AR очередь)** | `telegram_stars_shop_bot/docs/PLAN_LAVA_UNIFIED_HUB_2026-09-07.md` · autorenew `…/PLAN_VPN_LAVA_AUTORENEW_ALL_PERIODS_2026-09-06.md` · **Recurrent после ответа саппорта** |
| Order ref + nav back | `…/PLAN_BOT_ORDER_REF_VPN_NAV_2026-08-28.md` |
| Callback latency H1–H6 | `…/PLAN_BOT_CALLBACK_LATENCY_COMPETITOR_H1_H6_2026-08-28.md` |
| Incy + Happ | **§16** · `…/PLAN_INCY_SUPRA_LIGHT_STAGING_2026-08-16.md` |
| VPN для разработчика бота | `…/VPN_DEVELOPER_OVERVIEW_RU.md` |
| Рефералка / Drop | `…/REFERRAL_LEVELS_ANTIBUSE_CANON_2026-07-28.md` · `…/PLAN_GIVEAWAY_VPN_DROP_2026-08-15.md` |
| Product next level | `.cursor/PRODUCT_NEXT_LEVEL_TASK_REGISTRY.md` |
| Админка shop | `ADMIN_PANEL_UX_REBUILD_PLAN_RU.md` |

#### D. iOS / агенты / ops-память

| Тема | Файл |
|------|------|
| AGENTS.md | корень репо `AGENTS.md` |
| Ops-память | `CLAUDE.md` · `docs/ops-memory/` |
| Backend iOS API MAIN | `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md` |
| Cursor rules | `.cursor/rules/*.mdc` |

| **Доступ SSH (канон #3)** | `~/ALADDIN_VPN_SAFE/ENTRY_CLONE_KIT/SERVERS_ACCESS_CANON.md` · алиасы `aladdin-contabo` / `-sg` / `-mouth` / `aladdin-server` · ключ `~/.ssh/aladdin_server` |

---

## Оглавление

0. [30 секунд: мозг / дверь / двор / касса](#0-30-секунд-мозг--дверь--двор--касса) · [§0.3 Архитектура LIVE](#03-архитектура-vpn-live-2026-08-29--для-ml-анализ--починка)  
1. [Статус: сделано / осталось](#1-статус-сделано--осталось-2026-08-05)  
2. [Картинка одним взглядом + карта системы](#2-картинка-одним-взглядом)  
3. [Успешный пример: перенос двери 149→NEW](#3-успешный-пример-перенос-двери-149new)  
4. [Как быстро клонировать дверь на другой VPS](#4-как-быстро-клонировать-дверь-на-другой-vps)  
5. [Масштабирование (один мозг — много дверей)](#5-масштабирование-один-мозг--много-дверей)  
6. [На случай блокировки / давления (resilience)](#6-на-случай-блокировки--давления-на-vpn)  
7. [Платные опции P01–P05 подробно](#7-платные-опции-p01p05--что--зачем--как)  
8. [Backlog F01–F12 (бесплатно) + статусы](#8-backlog-f01f12--бесплатно)  
9. [GO / NO-GO / Rollback](#9-go--no-go--rollback)  
10. [Что говорить клиенту и поддержке](#10-что-говорить-клиенту-и-поддержке)  
11. [Шпаргалка команд](#11-шпаргалка-команд-без-секретов)  
12. [Запреты](#12-запреты)  
13. [Шесть шляп (кратко)](#13-шесть-шляп-кратко)  
14. [Скорость видео TikTok/IG — что пробовали 2026-08-13…14](#14-скорость-видео-tiktok--instagram--что-пробовали-2026-08-1314)  
15. [Shop Bot: архитектура кассы (Stars/Premium/VPN/реф/розыгрыш)](#15-shop-bot--архитектура-кассы-starspremiumvpnрефрозыгрыш) · [§15.8 `/start` soft-block](#158-бот-молчит-на-start--telegram-bot-api-soft-block--рот-mouth-prod) · [§15.9 VPN-кнопки / display_seq](#159-бот-молчит-на-vpn-кнопках--display_seq--db-lock--nameerror-не-soft-block)  
16. [Incy + Happ: клиенты, HWID, слоты 3 админов (2026-08-16)](#16-incy--happ-клиенты-hwid-слоты-3-админов-2026-08-16)  
17. [Касса LAVA: H2H ↔ classic — как устроено и как переключать](#17-касса-lava-h2h--classic--как-устроено-и-как-переключать)  
18. [P2 Bundle 10 профилей — Asia-via-NEW (2026-08-27)](#18-p2-bundle-10-профилей--asia-via-new-канон-2026-08-27) · [§18.8 LTE ночь](#188-инцидент-2026-08-28--ночь-wi-fi-ok--lte-всё-timeout-для-следующей-ml)  
19. [Глушилки LTE — негативные тесты 2026-08-28 (не повторять)](#19-глушилки-lte--негативные-тесты-2026-08-28--не-повторять) · jam-20 · HTTPS smoke · [§19.6 vk.com ban](#196-sni-policy--не-использовать-vkcom-2026-08-28-подтверждено-на-lte) · [§19.12 P01 Yandex LIVE](#1912-p01-yandex-ночная-дверь--live-staging-2026-09-11)

## 0. 30 секунд: мозг / дверь / двор / касса

| Роль | Простыми словами | Где сейчас (факт) |
|------|------------------|-------------------|
| **Мозг** | Бот, vpn-api, `vpn.db`, выдача `/sub/` | Contabo `185.225.233.150` |
| **Дверь (entry)** | Сюда стучатся клиенты Happ/Incy | **День / Wi‑Fi:** NEW `37.46.134.98` `:8444` · **Ночь staging LTE PASS:** NLB `84.201.151.20:443` → `yandex1` Reality → Brain (§19.12 · P01 §23) |
| **Двор (egress)** | Откуда VPN ходит в интернет | Contabo (тот же сервер-мозг) |
| **Труба** | WG lab дверь↔двор | NEW `10.10.0.3:51822` ↔ Brain `10.10.0.2:51821` · **P01** YC `10.10.0.6` ↔ тот же Brain |
| **Запасная дверь** | Откат ≤5 мин | **149** `149.154.65.180` — ещё **жива** (не stop 48–72ч) |
| **Касса** | Витрина + Lava + бот оплат | `aimonkeystars.ru` + `@AiMonkeyStars_bot` — **отдельно** от двери |

**Главный рычаг смены двери:** на Contabo  
`VPN_BRIDGE_PUBLIC_HOST=<IP_двери>` → `systemctl restart aladdin-shop-vpn-api` → клиентам: **обновить подписку в Happ или Incy**.

Клиенты (не два протокола): **Happ** (мир) + **Incy** (РФ) — одна `/sub/`, один VLESS Reality. Подробно → **§16**.

**Итог простым языком (устойчивость):**

| | |
|---|---|
| **Нельзя** | Надеяться, что «белый» RU‑IP спасёт навсегда. |
| **Нужно** | Две двери, инструкция клиенту, второй двор в запасе, касса отдельно. |
| **Порядок** | UX/готовность → GO на вход → egress и оплату **отдельно**. |
| **«Задушат»** | Не физика сети — станет дороже и нервнее **без** запасных дверей. |

**Пять машин (2026-08-26):** см. **§0.1** · **Rollout 2026-08-27:** backup → rot → bundle 10 prof (existing) → new VPS after LTE · three-way `VPN_JAMMING_THREE_WAY_DENDI_FROSTY_AIMONKEY_2026-08-26.md`

### 0.1 Распределение ролей (1 мост + 3 Contabo + MAIN)

| Имя | IP | Роль | Не путать с |
|-----|-----|------|-------------|
| **Мост NEW** | `37.46.134.98` | Prod VPN **дверь** 🇪🇺 `:8444` · 🌏 `:8445` · LTE `:5443` → WG → Brain/SG | Ночь LTE: IP часто режут · **запас** при P9 |
| **REG.RU ночь** | `92.242.61.63` | **P9 дверь** Reality `:443` + xHTTP `:8443` (staging→`jam-24b`) | Floating NIC · hop **через NEW** · handoff P9 |
| **Brain** | `185.225.233.150` | Мозг: бот, vpn-api, `/sub/`, egress EU | **Не** Vision всем (§14 FAIL) · **не** mass-entry |
| **Mouth** | `169.58.242.12` | **Bot API rot** (3proxy SOCKS `:1080`) · **prod ✅** | **Не** VPN door · **§15.8** |
| **SG** | `217.15.166.78` | Real **🇸🇬 egress** (Asia hop) | WG Brain↔SG · не client entry из РФ |
| **MAIN** | `149.154.65.180` | iOS `:8002` · VPN entry **снят** | Stop spare только `jam-72` + GO |

**Целевая / факт jamming:** P2 multi-profile ✅ · P9 REG staging PASS ✅ · мониторинг `jam-60…62` ✅ · fro-03/04 ✅ · CDN `jam-50/51` по GO · Contabo Vision всем ❌.

**Дополнение 2026-08-29 (не заменяет строки выше) — P9 REG PASS:**  
Дверь ночи = REG `…63`. Data-plane: телефон→REG→**NEW `:8444`**→WG→Brain. Прямой WG REG↔Brain на floating UDP нестабилен. Restore: `ML_SYSTEM_HANDOFF_P9_REG_RU_LTE_NIGHT_2026-08-29.md` · **§19.11** · Next: `jam-24b`.

**Дополнение 2026-09-01 — Ideal A закрыт:** REG OpenStack C\*/M\*/D\*: публичный IP только на виртуальном роутере (NAT); **вынести из-под NAT нельзя**. Не вешать `92.242.61.63` на ens3. `jam-22b` ❌. Канон hop-via-NEW **навсегда** для этой ВМ. Подробно: handoff P9 **§5.1**.

### 0.3 Архитектура VPN LIVE (2026-08-29) — для ML (анализ / починка)

> **Ничего выше не удалено.** Этот § — единая картина «как работает сейчас». Детали P9 → handoff; глушилки → канон #2; SSH → канон #3.

#### Control plane (кто выдаёт конфиг)

```text
Клиент Happ / Incy
  → HTTPS aimonkeystars.ru  (A → NEW …98, nginx)
       /          → сайт витрины
       /sub/<token> → proxy → Brain …150 :8091  (vpn-api)
                          ↓
                    vpn.db + subscription_bundle.py
                          ↓
                    JSON профилей (VLESS Reality outbounds + routing)
```

| Компонент | Где | Порт / путь |
|-----------|-----|-------------|
| vpn-api `/sub/` | Brain | `:8091` (с NEW nginx proxy) |
| Бот Stars/VPN | Brain | poller · Mouth SOCKS → Telegram API |
| HWID / слоты | Brain `vpn.db` | §16 |
| Касса Lava | Brain + aim | §17 |

**Рычаг смены адреса двери в профилях:** env Brain `VPN_BRIDGE_PUBLIC_HOST` / P9 flags / **`VPN_SUBSCRIBE_P01_*`** → `systemctl restart aladdin-shop-vpn-api` → клиент **обновить подписку**. P01 ключи Reality **свои** (не NEW/REG).

#### Data plane (куда идёт трафик приложений)

```text
═══ Профили на NEW (день / Wi‑Fi / запас) ═══
Телефон → NEW …98 :8444  (🇪🇺 Reality)  → WG 10.10.0.3→10.10.0.2:8446 → Brain egress EU
        → NEW …98 :8445  (🌏 Reality)  → hop → SG …78 egress 🇸🇬
        → NEW …98 :5443  (🇷🇺 LTE perekrestok) → contabo-hop → Brain

═══ Ночь P01 Yandex (staging; LTE PASS 12.09 ~04:47 через NLB) ═══
Сейчас в /sub/: телефон → NLB 84.201.151.20 :443 Reality
             → yandex1 :443 → WG 10.10.0.6 → Brain :8446 → egress …150
             NEW в этой цепочке НЕТ
Голый 158.x / HTTP-CDN: FAIL (режут IP / CDN не пронёс xHTTP)

═══ Профили P9 REG (старая ночь; при глушилках :443 FAIL) ═══
Телефон → REG …63 :443   (TCP Reality)     ─┐
        → REG …63 :8443  (xHTTP /xhttp-p9) ─┴→ REG outbound
                                              → NEW …98 :8444 (как клиент bridge)
                                              → WG NEW→Brain → egress …150
```

| Путь | Вход (телефон) | Hop | Exit IP |
|------|----------------|-----|---------|
| EU | NEW `:8444` | WG → Brain `:8446` | Brain `…150` |
| Asia | NEW `:8445` | NEW→SG | SG `…78` |
| LTE perek | NEW `:5443` | → Brain | Brain |
| **Ночь P01** | **сейчас `158.x:8443` · цель CDN `:443`** | **прямой WG YC→Brain** | Brain |
| **Ночь P9** | **REG `:443`/`:8443`** | **REG→NEW `:8444`→WG→Brain** | Brain |

**Запрещено путать:** Mouth/SG/MAIN — не вход Happ для ночи. Contabo Vision **напрямую с телефона** всем — §14 FAIL.

**Вердикт + gap до идеала + журнал LN A/B (2026-09-07):**  
`ML_SYSTEM_HANDOFF_VPN_IDEAL_GAP_AND_EXPERIMENTS_2026-09-07.md` — Contabo Wi‑Fi direct снова **FAIL** (минуты → N/A); daily Wi‑Fi = **🇩🇪 NEW**; Ideal = двери ASN/CDN + auto-pick, **не** 1-hop Contabo.

#### Взаимодействие сервисов (починка)

| Симптом | Куда смотреть | SSOT |
|---------|---------------|------|
| `/sub/` 502 / пусто | NEW nginx → Brain `:8091` · vpn-api · token | §11 · канон #3 |
| EU профили n/a | NEW xray-bridge · WG NEW↔Brain · Brain `:8446` | §18 · path-metrics |
| Asia n/a / не SG IP | NEW `:8445` · SG hop · WG Brain↔SG | §18 |
| Ночь LTE NEW timeout, Wi‑Fi OK | DPI на NEW IP — **ожидаемо** · ночь = **Яндекс** (P01), REG запас | §18.8 · §19.12 · P01 handoff |
| Ночь REG n/a при глушилках | **ожидаемо 2026-09-11** · не Ideal A · смотреть P01 | P01 handoff · P9 §5.1 |
| Ночь Яндекс n/a на `158.x` | ожидаемо (IP сожгли) · рабочая дверь = NLB `84.201.151.20` · если n/a на NLB → новый NLB, P01 §23.5 | §19.12 · P01 §23 |
| Бот молчит `/start` | Mouth SOCKS · soft-block (`getMe` висит) | §15.8 |
| **VPN-кнопки молчат**, `/start` иногда ок, webhook 200 | **Не soft-block:** `shop.db` lock · `display_seq` NULL · `NameError` в callback | **§15.9** · handoff 2026-09-04 |
| Оплата СБП | Lava H2H flag | §17 |
| Режут casino/ads | routing JSON fro-08/09 | `VPN_ROUTING_ADS_CASINO_PLAN_…` |

#### Юнит → сервер (systemd / быстрый SSH)

| Unit / процесс | Сервер | Зачем |
|----------------|--------|--------|
| `aladdin-telegram-bot` | **Brain** | Poller бота (единственный) |
| `aladdin-partner-api` · `aladdin-webhook-worker` | **Brain** | Касса `:8090` · webhooks |
| `aladdin-shop-vpn-api` · vpn workers | **Brain** | `/sub/` `:8091` · provision · `vpn.db` |
| `bot-mouth-3proxy` (SOCKS `:1080`) | **Mouth** | Рот Bot API (§15.8) |
| `xray-bridge` · `wg-quick@wg-bridge-lab` · `nginx` | **NEW** | Дверь 🇪🇺/🌏/LTE · proxy `/sub/` |
| `xray-bridge` · `wg-quick@wg-p01-yc` | **YC** `158.160.24.238` | Ночь `:443` → Brain `10.10.0.2` |
| xray P9 (`:443` / `:8443`) | **REG** | Старая ночь → hop NEW (глушилки: `:443` FAIL) |
| WG/xray Asia hop egress | **SG** | Exit 🇸🇬 для `:8445` |
| iOS API `:8002` · (VPN entry **снят**) | **MAIN** | Не poller бота · не дверь Happ |

#### Код SSOT (репо)

| Слой | Путь |
|------|------|
| Bundle / P9 | `aladdin_shop_vpn_api/subscription_bundle.py` · `subscription_util.py` · `settings.py` |
| Routing | `routing_ru_direct.json` · `routing_casino_slots.json` |
| Deploy scripts | `deploy/scripts/apply_jam_p9_staging.sh` · `apply_fro09_*` · `apply_fro08_*` |
| Bot silent / display_seq | `telegram_stars_shop_bot/bot/services/orders_repo.py` · `bot/db/database.py` |

---

## 1. Статус: сделано / осталось (обновлено 2026-09-11)

### 1.1 ✅ Сделано

| # | Блок | Факт |
|---|------|------|
| 1 | NEW VPS + DNS + HTTPS | `aimonkeystars.ru` → `37.46.134.98` |
| 2 | nginx NEW | сайт + proxy `/sub/` → Contabo |
| 3 | xray-bridge NEW | `:8444` → hop `10.10.0.2:8446` |
| 4 | WG lab | peer Contabo `10.10.0.3` ↔ NEW `wg-bridge-lab` `:51822` |
| 5 | Prep + **T1** | `PREP_WG_LAB_…`, **`PRE_CUTOVER_T1_20260805-114243`** + `ROLLBACK.md` (Contabo/149/NEW/Mac) |
| 6 | **GO CUTOVER** | `VPN_BRIDGE_PUBLIC_HOST=37.46.134.98`; `/sub/` address=NEW; 15м watch |
| 7 | Канал | `@monkeystarspremium`: обновить подписку |
| 8 | Ops | path-metrics NEW **1ч**; `/vpn_health`→NEW; digest **1ч** |
| 9 | Витрина | get→aim A–F; **Lava Success/Fail→aim** ✅; legal aim ✅; compat aladdin `/sub/` |
| 10 | Админка | A0–A8 + FIN + kind×period |
| 11 | GREEN_POINT bak | Contabo+149+NEW+Mac |
| 12 | HWID stubs | «Лимит-устройств» ≠ «HWID-занят-другим-аккаунтом» |
| 13 | `ru_direct` | Ozon/WB/банки мимо VPN |
| 14 | **Speed hybrid campaign** | 2026-08-13…14: прямой Wi‑Fi Vision **не взлетел**; MTU без выигрыша; гибрид **откатили**; прод = один **🇩🇪 Германия** (мост NEW). Итог → **§14** |
| 15 | **Shop Bot карта** | §15 — касса Contabo |
| 16 | **Incy Supra light** | 2026-08-16: Incy рядом с Happ; `MODE=all`; канон устройств B (лимит 1); self-reset; 3 админа → `device_limit=5`. Итог → **§16** |
| 17 | **Касса LAVA** | 2026-08-17: СБП H2H (QR НСПК) + карта classic a817; флаг `LAVA_H2H_SBP_ENABLED`. Итог → **§17** |
| 18 | **P2 Asia-via-NEW + 10 prof** | 2026-08-27: 🇪🇺×5 NEW`:8444`→Brain · 🌏×5 NEW`:8445`→SG · staging PASS 10/10 · `jam-34` → `MODE=all` · пользователям обновить `/sub/`. Итог → **§18** |
| 19 | **P9 REG ночь** | 2026-08-29 staging PASS · REG `…63` `:443`/`:8443` → hop NEW `:8444` → Brain. Итог → **§19.11** · handoff P9 |
| 20 | **Ideal A ❌** | 2026-09-01: REG OpenStack NAT · `…63` не на NIC · hop-via-NEW **навсегда** на этой ВМ · `jam-22b` cancelled |
| 21 | **Bot silent display_seq** | 2026-09-04: NULL `display_seq` → lock → `NameError` → VPN-кнопки молчат; hotfix + P0 stamp/migrate; Contabo deploy. Итог → **§15.9** |
| 22 | **LN A/B + ideal-gap doc** | 2026-09-07: LTE×3 **PASS** (без глушилок); Contabo «Домашний Wi‑Fi» снова **FAIL** blackhole; handoff ideal I1–I9. Итог → `ML_SYSTEM_HANDOFF_VPN_IDEAL_GAP_AND_EXPERIMENTS_2026-09-07.md` |
| 23 | **P01 Yandex ночь** | NLB `84.201.151.20:443` · owner LTE **PASS 12.09 ~04:47** · всем нет (`p01-yc-10`). Итог → **§19.12** · P01 **§23** |

### 1.2 ⏳ Осталось (VPN + resilience + скорость)

| ID | Задача | Кто |
|----|--------|-----|
| A | Happ: Reels/TT 30с на **🇩🇪 Германия** (Wi‑Fi + LTE) — зафиксировать «тормозит / ок» | владелец |
| B | TG: `/vpn_health` (Contabo CF «плавает» = шум спот-теста, см. §14.4) | владелец |
| C | 48–72ч наблюдение entry | ops |
| D | Stop bridge на **149** (явный GO) | после C |
| E | Сейф post-cutover | после D |
| **S1** | Улучшить path-metrics (медиана 2–3 CF / писать load) — меньше ложных «плавает» | ops/bot |
| **S2** | tunnel_speed CSV + Happ: понять буфер видео на **мосту** (не Contabo→CF) | ops |
| **S3** | Опц. xhttp/CDN профиль **staging** — только если нужен 2-й путь без Vision-direct | по GO · ideal **I4** |
| **S4** | NL / 2-й egress (**P02**) — только если S2 показал разрыв «в разы» vs Save | по GO · §7 P02 · ideal **I6** |
| **LN1** | Contabo «Домашний Wi‑Fi» — **снят с `/sub/` 14.09**. Был только у владельца (hybrid staging). **FAIL** blackhole, не Германия. Не включать `HYBRID_WIFI_STAGING` снова | **сделано** |
| **LN2** | Тест Wi‑Fi → профиль **🇷🇺 LTE — для ночи** (REG) 5–10 мин TG/IG | владелец · ideal **I2** |
| **LN3** | Повтор LTE drill при глушилках | **PASS 12.09 ~04:47** NLB `84.201.151.20` · голый `158.x` FAIL |
| **F02** | Текст в боте «если не коннектится» (4 шага) | bot UX |
| **F03** | Кнопка «Обновить доступ» / запасная ссылка | bot |
| **F04** | Та же инструкция на aim | сайт |
| **F09** | 15 мин/неделя — новости / оферта хостера | владелец |
| **F10** | Заготовки ответов поддержке | support |
| **P01 / jam-24b** | **LIVE 13.09:** всем «🇷🇺 LTE — ночной вход» · `MODE=all` · NLB `84.201.151.20:443` · P01 **§23.4** | сделано |
| **vpn-zd-13e…14** | Guard v2 + expiry retry + безопасный prune + OPS digest + sync MAIN/REG по динамическому `N` + наблюдение | **следующая фаза 2026-09-10** |
| **jam-71** | В самом конце: «Авто‑обход» + ручные серверы остаются; без нового VPS/ASN | после zero-downtime fix и наблюдения |
| **P02…P05** | Остальные платные опции — только по отдельному GO (см. §7) | когда нужно |
| G | Control plane bot+db на RU | отдельный проект |

### 1.3 Ответы на частые вопросы «сделали ли?»

| Вопрос | Ответ |
|--------|--------|
| Свежий **PRE_CUTOVER_T1** Contabo/149/NEW/Mac + ROLLBACK? | ✅ да, `PRE_CUTOVER_T1_20260805-114243` |
| Cutover только по **GO CUTOVER**? | ✅ да; HOST→NEW; Happ; 15м watch |
| В главном файле расписано мозг/двери/клон? | ✅ этот файл (§0, §3, §4, §5) |
| Бот молчит, но getMe/webhook живы? | ✅ **§15.9** (не путать с soft-block §15.8) |
| Архитектура «идеальна»? Что допилить? | **Нет** — правильная топология. Gap I1–I9 → `ML_SYSTEM_HANDOFF_VPN_IDEAL_GAP_AND_EXPERIMENTS_2026-09-07.md` |
| Contabo «Домашний Wi‑Fi» | **не рабочий.** Снят с `/sub/` 14.09 (`HYBRID_WIFI_STAGING=false`). Был только у владельца. Daily Wi‑Fi = **🇩🇪 Германия** |
| Ночь LTE при глушилках 2026-09-11 / 12? | 11.09 Яндекс **PASS**. **12.09 ~02:07 LTE FAIL** на голый `158.x`; Wi‑Fi/Германия **PASS**. Дальше CDN. Всем — нет. SSOT: P01 §0 |
| Детали cutover-окна | `CUTOVER_149_TO_NEW_RUNBOOK_RU.md` |
| Фазы миграции 0–12 | `VPN_RU_ENTRY_SPLIT_MIGRATION_PLAN_RU.md` §2.1b |

---

## 2. Картинка одним взглядом

```text
Телефон (Happ)
    → ДВЕРЬ (entry)     ← P01 = вторая дверь (другой хостер/ASN)
    → ДВОР  (egress)    ← P02 = второй двор / другой IP двора
    → интернет

Ссылка /sub/...         ← P03 = вторая «записка с адресом» (домен только для /sub/)

КАССА (отдельно): aimonkeystars.ru + Lava + бот
    ← P05 = второй канал оплаты (не в одном окне с дверью)
```

**Дверь** — с чего клиент в РФ «заходит» в VPN.  
**Двор** — Европа (Contabo), откуда уже интернет.  
**/sub/** — пропуск в Happ; домен в ссылке — адрес на конверте.  
**Мозг** — Contabo: кто выдаёт пропуск и хранит аккаунты.

```text
Телефон (Happ)
    │  /sub/ JSON (address = VPN_BRIDGE_PUBLIC_HOST)
    ▼
 NEW 37.46.134.98 :8444   xray-bridge     ← активная дверь
    │
    │  WG lab 10.10.0.3:51822  ←→  Contabo 10.10.0.2:51821
    ▼
 Contabo 185.225.233.150                  ← мозг + двор
    ├── vpn-api :8091
    ├── xray/WG users :8446 / wg0
    └── telegram bot (ОДИН polling)

Запас: 149 :8444 + wg 10.10.0.1           ← тёплый rollback
```

| Роль | Сейчас | Заметка |
|------|--------|---------|
| Витрина / legal | `aimonkeystars.ru` | Канон магазина |
| Entry прод | **`37…:8444`** | После cutover 2026-08-05 |
| Entry запас | `149…:8444` | Не stop до GO фазы 9 |
| Egress | Contabo | Один основной двор |
| Split RU | `ru_direct` | Уже плюс |

---


### 2.1 Дополнение 2026-08-27 — две двери на NEW (EU + Asia hop)

```text
Телефон Happ/Incy (одна /sub/)
    │
    ├─► NEW 37.46.134.98 :8444  «🇩🇪…🇸🇪»  ──WG──► Brain 185… :8446 ──► интернет (EU IP)
    │
    └─► NEW 37.46.134.98 :8445  «🇸🇬…🇹🇭»  ──sg-hop Reality──► SG 217… :443 ──► интернет (Сингапур)
              (Reality моста, SNI max.ru)              (телефон Contabo не видит)

Brain: vpn-api /sub/ · VPN_ASIA_ENTRY_MODE=via_new · MULTI_COUNTRY_MODE=all (после jam-34)
SG: только egress + hop-UUID (не client entry из РФ)
MAIN 149: iOS API — VPN entry не трогаем в P2
```

**Выяснено в работе (важно для ML):**

1. Прямой вход телефона на Contabo SG `:443` из РФ → кратко OK, потом **ping n/a / blackhole** (ASN Contabo на входе).  
2. Лечение: **тот же стабильный вход NEW**, отдельный порт **`:8445`**, hop на SG → exit IP = `217.15.166.78`.  
3. В Happ адрес Азии = **NEW**, не `217…78`; имена флагов 🇸🇬🇯🇵… — UX; реальный Asia IP = Сингапур.  
4. EU и Asia на NEW: **одинаковые Reality-ключи моста**, SNI клиента `max.ru` (serverNames inbound).  
5. Peer-sync кладёт UUID во **все** vless inbound NEW (`:8444` и `:8445`).  
6. `multi_country` имеет приоритет над `elimination=bridge_only` в `subscription_bundle.py`.  
7. Staging-first: сначала TID `493897224` Wi‑Fi+LTE **10/10**, затем `jam-34` → `MODE=all`.  
8. Пользователям нужно **обновить подписку** в Happ/Incy (тот же URL `/sub/`).

## 3. Успешный пример: перенос двери 149→NEW

### 3.1 Что сделали в день окна (хронология UTC)

| Время | Событие |
|-------|---------|
| prep ~11:42 | `wg-bridge-lab` enable+start; ping ~45–47 ms; HOST ещё 149 |
| T1 ~11:42 | bak Contabo/149/NEW + Mac + `ROLLBACK.md` |
| **GO** ~11:51 | `VPN_BRIDGE_PUBLIC_HOST=37.46.134.98`; restart vpn-api; `/sub/`→NEW |
| | Пост в канал; **149 не stop** |
| ~12:05 | Watch: lab traffic↑; services OK |
| ~12:12 | Metrics+`/vpn_health`→NEW |
| ~12:17 | Digest/cron = 1 час |

**Первый замер NEW:** CF ~11 MB/s, RTT ~43 ms, swap 0%, sessions ~67.

### 3.2 Пошагово (как повторить)

1. Prep: дверь рядом жива; handshake Contabo↔lab; HOST ещё старый.  
2. T1 bak + ROLLBACK.md.  
3. Только по фразе владельца **`GO CUTOVER`**: HOST→новый IP; restart vpn-api.  
4. Проверка `/sub/` address = новый IP.  
5. Happ refresh + 15м watch.  
6. 48–72ч → отдельный GO на stop старой двери.  

**Откат ≤5 мин:** HOST→старый IP из T1 → restart vpn-api → Happ refresh. Старую дверь не гасить заранее.

---

## 4. Как быстро клонировать дверь на другой VPS

Цель: **Entry-N+1** рядом → один HOST flip. Мозг **не** копируем.

**Ночь P01 (Yandex `:443` → сразу Brain):** не этот §4 (он про клон **NEW `:8444`**). Рецепт клона ночи — P01 handoff **§11.2**. Набор файлов: `~/ALADDIN_VPN_SAFE/P01_GOLDEN_DOOR_KIT/` (**собрано 2026-09-12**). Следующий туннель при новом ВМ: **`10.10.0.7`**. Самый быстрый reroll — новый IP на том же `yandex1`, WG `10.10.0.6` не менять.

### 4.1 Что копируем с эталона (NEW)

| Артефакт | Путь | Назначение |
|----------|------|------------|
| xray-bridge config | `/opt/xray-bridge/config.json` | `:8444` → hop Contabo |
| systemd | `xray-bridge.service` | автозапуск |
| WG lab | `/etc/wireguard/wg-bridge-lab.conf` | **новые** ключи + **новый** `10.10.0.x` |
| pulse | `/usr/local/bin/aimonkey-vpn-pulse.sh` + cron `*/5` | пульс |
| path-metrics | `/usr/local/bin/vpn_path_host_metrics.sh` + cron `5 * * * *` | CF/RTT/swap |
| nginx | опционально (сайт) | entry-only можно без сайта |
| UFW | `8444/tcp`, `WG_PORT/udp` | двери |

На клоне WG-ключи **новые**. Reality public params согласовать с выдачей vpn-api.

### 4.2 Порядок (лучший)

**Шаг 0.** Свободный tunnel IP (у нас `.1`=149, `.2`=Contabo, `.3`=NEW → далее `.4`) и свободный WG ListenPort (`.3`→51822; далее например 51823).

**Шаг 1.** VPS (≥2–4 GiB), порты, SSH владельца + **pubkey Contabo** в `authorized_keys`.

**Шаг 2.** WG на новом VPS + peer на Contabo → ping двусторонний.

**Шаг 3.** xray-bridge (hop = `10.10.0.2:8446`) → LISTEN `:8444`.

**Шаг 4.** pulse + path-metrics (`VPN_METRICS_HOST_ROLE=newru` или `entryN`).

**Шаг 5.** T1 bak + ROLLBACK.

**Шаг 6.** Только по GO: HOST→новый IP; bot health host→новый IP; пост «обновите подписку»; старую дверь не stop 48–72ч.

**Шаг 7.** Откат = HOST назад.

### 4.3 Чеклист «дверь готова»

| Проверка | GO |
|----------|-----|
| ping Contabo ↔ tunnel IP | OK |
| `wg` handshake &lt;2 мин | OK |
| `:8444` LISTEN | OK |
| Contabo `/ready` | ready |
| `/sub/` address = новый IP | да |
| Старая дверь active | да |
| Один bot polling | да |
| Секреты не в чате/git | да |

---

## 5. Масштабирование: один мозг — много дверей

### 5.1 Принципы

1. Один мозг: один `vpn.db`, один bot polling, один vpn-api.  
2. Много дверей: только data-plane (xray+WG).  
3. Рядом → потом HOST flip.  
4. Откат дешевле лечения (старая дверь 48–72ч).  
5. Не мешать окна (entry / Lava / routing / egress).  
6. Compat aladdin `/sub/` ≥90 дней.  
7. Наблюдаемость: pulse + metrics + digest/час + `/vpn_health`.  
8. IP-план в сейфе.

### 5.2 Рост

| Этап | Что | Зачем |
|------|-----|-------|
| Entry-1 (NEW) | одна дверь | прод сейчас |
| Entry-2 (P01) | другой хостер/ASN | failover при блоке двери |
| DNS multi (позже) | только если api умеет разным host | иначе явный HOST flip |
| CP на RU | bot+db | **не** клон двери |

Пока один `VPN_BRIDGE_PUBLIC_HOST` → модель «активная + тёплый резерв», не автоматический баланс всех клиентов.

### 5.3 Пакет клона в сейфе

`~/ALADDIN_VPN_SAFE/ENTRY_CLONE_KIT/` — **не** один файл; три канона + зеркала:

| Файл в сейфе | Роль |
|--------------|------|
| `README.md` | Зеркало **этого** главного playbook (канон #1) |
| `VPN_JAMMING_DENDI_VS_AIMONKEY_ANALYSIS_AND_PLAN_2026-08-20.md` | Копия канона #2 (глушилки / Dendi) |
| `SERVERS_ACCESS_CANON.md` → `SERVERS_ACCESS_CANON_ML_2026-08-26.md` | Канон #3: SSH, IP, пароли (**только сейф**) |
| `PAYMENTS_LAVA_H2H_CLASSIC_PLAYBOOK_RU.md` | Касса LAVA |
| `ML_SYSTEM_HANDOFF_TELEGRAM_BOTAPI_SOFTBLOCK.md` | Бот молчит на `/start` |

Также: templates xray/wg, pulse/metrics, cutover/rollback scripts (без private keys в открытом виде).  
**Ночь P01 (отдельная папка сейфа):** `~/ALADDIN_VPN_SAFE/P01_GOLDEN_DOOR_KIT/` — бинарь Xray 26.3.27 + sanitized JSON + WG `10.10.0.7` + jam-21. Ключей живой двери нет.  
**Не склеивать** три канона в один README; **не** класть `VPN_SPEED_DEGRADATION_HANDOFF_RU.md` §32 в git.

### 5.4 Автоматизация минимума

```bash
# cutover_to.sh <IP>  — bak env → set HOST → restart vpn-api → ready → «обновите подписку»
```

Провижин автоматизировать только файлы **двери**, не brain.

---

## 6. На случай блокировки / давления на VPN

*(Включено из `VPN_RESILIENCE_MINPLAN_RU.md` — статусы обновлены 2026-08-05.)*

### 6.1 Одной фразой

Не маскироваться сильнее под «легитимный IP», а уметь **за минуты сменить вход** и объяснить клиенту, что нажать.

### 6.2 Что делать при симптомах

| Симптом | Скорее всего | Действие |
|---------|--------------|----------|
| Happ не коннектится, `/sub/` обновляется, address=дверь, TCP двери мёртв | Режут **дверь** (entry) | Failover на запасную дверь (149 пока жива / P01) + HOST flip + «обновите подписку» |
| Дверь TCP OK, но «интернет через VPN» мёртвый / Contabo CF падает | Режут **двор** (egress/ASN) | Lab **P02**, отдельно от смены двери |
| Серверы живы, `/sub/` по домену не открывается | Режут **имя** (DNS/SNI) | **P03** зеркало домена только для `/sub/` |
| Магазин/оплата ок, VPN нет | Касса отдельно — хорошо | Чинить только VPN-путь |
| Всё упало сразу после смены Lava+HOST+routing | Смешали окна | Откат по одному рычагу; правило F08 |

### 6.3 Порядок работ (не нарушать)

```text
1) F02 F03 F04 (+ F10)     ← UX клиенту (ещё не всё сделано)
2) F06 F07                 ← ✅ lab/smoke + T1 уже были; держать свежими
3) P01 lab (если нужен другой ASN)
4) GO владельца            ← переключение entry
5) P02 lab egress          ← отдельно
6) P03 зеркало /sub/       ← отдельно
7) Оплата / Lava           ← отдельно (get-E уже ✅ на aim)
```

### 6.4 Следующая фаза: Guard v2 + add-only

Начать 2026-09-10 до остальных VPN-фаз:

1. `vpn-zd-13e-guard-v2-tests` — ✅ локальные RED/GREEN, 30 PASS;
2. `vpn-zd-13f-guard-v2-add-only` — ✅ локально: audit + add missing active;
3. `vpn-zd-13g-guard-safe-env` — ✅ локально: parser без `source` + freshness alert;
4. `vpn-zd-13k-expiry-retry-alerts` — ✅ локально: strict exit code, retry job, final OPS alert;
5. `vpn-zd-13l-daily-ops-report` — ✅ → **Command Center ×3** (09/14/21 МСК) всем `ADMIN_IDS`; runbook `VPN_OPS_COMMAND_CENTER_RU.md`;
6. `vpn-zd-13m-known-zombie-prune` — ✅ локально: удалять только доказанные expired/revoked; unknown сохранять;
7. `vpn-zd-13h-deploy-guard-v2` — ✅ backup, audit-only и controlled deploy;
8. `vpn-zd-13i-add-only-sync` — ✅ `35` unique active восстановлены, `42` strict-terminal удалены;
9. `vpn-zd-13j-verify-79` — initial PASS; timer-cycle evidence in progress;
10. `vpn-zd-14-watch` — 30 минут и два smoke-цикла без restart;
11. `vpn-zd-13n-main-nightly-restart-off` — после стабильности отдельным GO отключить restart MAIN 04:30.

Gate 1 audit-only 2026-09-09: `N=81`; missing unique `35`; terminal unique
`42` (`expired=41`, `manual_override=1`); unknown unique `6` сохранены;
действий `add=0/remove=0`, errors `0`, Xray unchanged.

Gate 2 2026-09-09: `66` door-add операций; `42` strict-terminal UUID
удалены (`52` door-remove операций); unknown `6` сохранены. Второй цикл
`add=0/remove=0/errors=0`; config/Reality/14-profile smoke PASS; restart Xray
`0`. Smoke UUID healed на MAIN/REG; E2E PASS: NEW EU/Asia, MAIN warm
`:8444`, REG `:443`. Timers: Guard `*/15`, stale watchdog `*/10`, OPS
Command Center digest `09:00 / 14:00 / 21:00 МСК` → `ADMIN_IDS`; hourly cron отключён.

Полный канон и причины:
`VPN_XRAY_ZERO_DOWNTIME_USER_SYNC_RUNBOOK_2026-09-08.md` §8.

Запрет: scheduled guard не удаляет extra/unknown UUID и не вызывает restart.

---

## 7. Платные опции P01–P05 — что / зачем / как

Платить после бесплатного UX/готовности **или** при живом инциденте.

### P01 — Запасной entry (другой хостер / ASN)

> **LIVE 2026-09-11:** Yandex Cloud Москва `158.160.24.238:443` · прямой WG `10.10.0.6`→Brain · профиль **🇷🇺 LTE — Яндекс ночь** · staging TID `493897224` · владелец LTE **PASS**.  
> SSOT: `ML_SYSTEM_HANDOFF_P01_YANDEX_NIGHT_DOOR_2026-09-11.md` · этот файл **§19.12**.  
> Запись 2026-09-09 «не добавляем» снята.

**Что сделано:** вторая дверь **другого ASN** (Yandex AS200350, не клон REG/NEW). Двор (Brain) тот же. Hop через NEW **нет**.  
**Зачем было:** ночной REG `:443` при глушилках мёртв (вахта + Германия).  
**Что осталось платить/решать:** не новую ВМ, а **GO всем** (`p01-yc-10`) или второй IP, если этот сожгут.  
**Не делать:** ещё один REG; Ideal A; Contabo как вход; карусель новых IPv4; `MODE=all` без GO. CDN Mops — **текущий шаг** (кабинет владельца, не jam-50).  
**Клон двери вообще:** §4 (для *следующей* ВМ, не для уже живого Yandex).

### P02 — Второй egress / доп. IP Contabo (сначала lab)

| Вариант | Смысл |
|---------|--------|
| Доп. IP Contabo | Тот же двор, другой «номер дома» |
| Второй VPS (другая страна) | Настоящий запасной двор — сильнее, дороже |

**Зачем:** режут выход в Европе, а дверь в РФ жива.  
**Как:** lab → свой Happ → GO на прод → «обновите подписку». **Отдельно** от P01 и Lava.  
**Детали:** `VPN76_RESERVE_EGRESS_RUNBOOK.md`.  
**Не делать:** менять двор и дверь в один вечер.

### P03 — Домен‑зеркало только для `/sub/`

**Что:** второй домен **только** для ссылок подписки (не магазин, не касса).  
Пример: `https://aimonkeystars.ru/sub/…` → запас `https://vpn-xxx.ru/sub/…` (тот же backend).  
**Зачем:** режут имя в ссылке.  
**Как:** DNS → тот же vpn-api; кнопка «Запасная ссылка» в боте; legal/Lava остаются на aim. GO отдельно от P01/P02.

### P04 — Внешний мониторинг entry

Uptime TCP/HTTP с нескольких стран → раньше узнать, что дверь умерла.

### P05 — Второй канал оплаты

Касса жива, если один эквайринг отвалился. **Отдельный проект**, не ночь с entry.

### Что выбрать

| Ситуация | Включать |
|----------|----------|
| Режут вход РФ / хостер | **P01** |
| Вход ок, «интернет VPN» мёртв / Contabo в бане | **P02** |
| Серверы живы, домен `/sub/` режут | **P03** |
| Пока спокойно | UX F02–F04; из платного чаще готовят **P01** |

**Лучший порядок оплаты:** P01 (lab) → при нужде P03 → P02 lab; каждый раз отдельный GO на прод.  
**Золотое правило:** касса (aim + Lava) **не** переезжает вместе с дверью/двором/зеркалом `/sub/`.

---

## 8. Backlog F01–F12 — бесплатно

| ID | Задача | Статус 2026-08-05 |
|----|--------|-------------------|
| F01 | MD‑план устойчивости | ✅ (влит в этот главный файл) |
| F02 | Текст в боте «если не коннектится» (4 шага) | ⬜ |
| F03 | Кнопка «Обновить доступ» / запасная ссылка | ⬜ |
| F04 | Та же инструкция на aim | ⬜ |
| F05 | Чеклист GO/NO‑GO | ✅ (§9) |
| F06 | Smoke lab entry 37… | ✅ (и cutover на 37… выполнен) |
| F07 | Бэкапы + rollback | ✅ T1 + ROLLBACK + GREEN_POINT |
| F08 | Не мешать cutover + Lava + routing | ✅ соблюдать (правило) |
| F09 | 15 мин/неделя — новости / оферта хостера | ⬜ |
| F10 | Заготовки ответов поддержке | ⬜ |
| F11 | Lava Success/Fail на aim | ✅ get-E |
| F12 | Legal на aim | ✅ |

**Платно (по GO):** P01…P05 — §7.

**Не трогать без отдельного GO:** stop bridge 149 (ещё рано); RAM на 149; удаление aladdin `/sub/`.

Следующий удобный шаг агента по UX: **F02+F03** — только после вашего **GO**.

---

## 9. GO / NO-GO / Rollback

### Готовность (всегда)

| # | Проверка |
|---|----------|
| 1 | Бэкап entry/env известен (T1 / сейф) |
| 2 | Запасная дверь или новая lab PASS |
| 3 | Тестовый Happ на целевом входе |
| 4 | Текст/кнопка клиенту (F02/F03) — желательно до массового failover |
| 5 | Откат описан (HOST назад) |
| 6 | Сегодня **нет** смены Lava URL и routing |

### GO на прод-переключение входа

| | |
|---|---|
| **GO** | Владелец сказал явную фразу (`GO CUTOVER` / «переключай entry»); smoke зелёный; ROLLBACK под рукой; поддержка/канал в курсе |
| **NO-GO** | Нет бэкапа; lab не проверен; одновременно Lava/routing; RAM 149 «заодно»; нет текста клиентам |

### Rollback

1. Вернуть старый `VPN_BRIDGE_PUBLIC_HOST`.  
2. `systemctl restart aladdin-shop-vpn-api`.  
3. Клиентам: обновить подписку в Happ.  
4. Smoke + пост.  

Техника failover: `VPN65_BRIDGE_FAILOVER_RUNBOOK.md`.

---

## 10. Что говорить клиенту и поддержке

**Если VPN не подключается:**

1. Откройте Happ.  
2. Обновите подписку (pull to refresh / Update).  
3. Если не помогло — в боте «Обновить доступ» / запасная ссылка (когда F03 будет).  
4. Банки, Госуслуги, Ozon, Wildberries — лучше **без** VPN (`ru_direct` уже помогает, но привычка важна).  
5. Напишите в Поддержку номер заказа.

Пост cutover (уже уходил в канал): короткое обновление входа 5–15 мин → обновить подписку; ждать «починки» не нужно.

---

## 11. Шпаргалка команд (без секретов)

```bash
# Contabo — активная дверь
grep ^VPN_BRIDGE_PUBLIC_HOST= /opt/aladdin-shop-vpn-api/env
curl -sS -m5 http://127.0.0.1:8091/ready
wg show wg-bridge

# NEW
systemctl is-active xray-bridge wg-quick@wg-bridge-lab nginx
ping -c2 10.10.0.2

# P01 Yandex night door (yc-user@158.160.24.238)
# systemctl is-active xray-bridge wg-quick@wg-p01-yc
# ping -c2 10.10.0.2
# Brain: wg show wg-bridge | grep -A3 10.10.0.6
# grep -E '^VPN_SUBSCRIBE_P01_|^VPN_P01_' /opt/aladdin-shop-vpn-api/env | sed 's/=.*/=***/'

# Cutover
# sed HOST=NEW_IP; systemctl restart aladdin-shop-vpn-api

# Rollback
# sed HOST=PREV_IP; systemctl restart aladdin-shop-vpn-api
```

Бот (Contabo shop `.env`):

```text
VPN_BRIDGE_HEALTH_HOST=<active_entry_ip>
VPN_PATH_METRICS_REMOTE_HOST=<active_entry_ip>
VPN_PATH_DIGEST_ENABLED=true
VPN_PATH_DIGEST_INTERVAL_SECONDS=3600
```

---

## 12. Запреты

- Второй bot polling / вторая главная `vpn.db`  
- Stop старой двери в минуту cutover  
- HOST + Lava + routing (+ egress) в одном окне  
- Один WG peer/IP на два публичных сервера  
- Удаление compat aladdin `/sub/` без плана  
- Стратегия «залезть в белый список» как главная страховка  
- RAM‑апгрейд 149 без отдельного решения  
- Секреты в чат/git  
- **SNI `vk.com` / `www.vk.com` в `/sub/`** — LTE FAIL на non-VK IP (§19.6); только `max.ru` / `yandex.ru` / `cloudflare` по политике

---

## 13. Шесть шляп (кратко)

| Шляпа | Смысл |
|-------|--------|
| Белая | Давят на «белые» IP; у нас дверь/двор/касса разделены |
| Красная | Клиенту страшнее «непонятно что делать» |
| Чёрная | Одна дверь = SPOF; мешать окна опасно |
| Жёлтая | Архитектура, `ru_direct`, бэкапы, Happ refresh |
| Зелёная | Дверь А/Б, lab egress, запасная оплата |
| Синяя | Сначала UX/готовность; большие шаги только по GO |

---

## Приложение A — минимальный план по неделям (ориентир)

**Неделя 1:** F02–F04, F10, F09 напоминание; держать F06/F07 актуальными.  
**При риске ASN двери:** P01 lab → личный smoke → GO.  
**Дальше:** P02/P03 по симптомам; stop 149 после 48–72ч спокойствия; CP на RU — отдельный проект.  
**Скорость видео:** см. **§14** (не путать Contabo CF «плавает» с буфером Reels).

---

## 14. Скорость видео (TikTok / Instagram) — что пробовали 2026-08-13…14

> **§14 = история кампании скорости (hybrid FAIL).**  
> **Прод-профили Happ/Incy сейчас = §18** (10 профилей: 🇪🇺×5 + 🌏×5), не «один 🇩🇪» из таблицы 14.2.  
> Для другой ML: канон-итог hybrid / stream-speed.  
> Детали плана: `telegram_stars_shop_bot/docs/PLAN_VPN_STREAM_SPEED_HYBRID_2026-08-13.md`  
> Handoff сессии: `telegram_stars_shop_bot/docs/ML_SYSTEM_HANDOFF_VPN_STREAM_SPEED_HYBRID_2026-08-14.md`  
> Пре-бэкап: `~/ALADDIN_VPN_SAFE/stream_speed_prebackup_20260813_234953/` (SHA verify OK)  
> **Не** склеивать сюда `VPN_SPEED_DEGRADATION_HANDOFF_RU.md` (§32 secrets). Открывать только для recovery/ключей; помнить: **дверь = NEW**, не 149.

### 14.1 Почему в боте «Contabo плавает 3…14 MB/s», а видео всё равно может тормозить

| | Contabo CF в `/vpn_health` | Видео в IG / TikTok |
|---|---|---|
| Что меряем | Contabo раз в час качает 20 MB с **Cloudflare** | Телефон → **дверь NEW** → WG → Contabo → **CDN TikTok/IG** |
| Смысл | Спот-тест **двора** (egress) | Реальный путь пользователя + CDN + буфер приложения |
| Типичные цифры | медиана ~**10 MB/s**, разброс 3…20 нормален | Нужно стабильно ~5–15+ Mbps **на телефоне** без обрывов TCP |
| Вывод | «Плавает» ≠ Contabo сломан | Тормоза видео часто из **двойного hop + DPI/LTE + CDN**, не из одной строки CF |

**Простыми словами:** бот смотрит «насколько двор Contabo сегодня быстро качает тестовый файл».  
Видео идёт **другим маршрутом** (ещё дверь в РФ + мост). Поэтому CF может быть «норм/плавает», а Reels всё равно буферится — и наоборот.

### 14.2 Что оставили в проде (итог 2026-08-14 вечер)

> **Исторический снимок кампании.** После **§18 (2026-08-27)** у всех **10 профилей** (🇪🇺×5 + 🌏×5), не один «🇩🇪 Германия». Таблица ниже — что было **вечером 14.08** после отката hybrid.

| Параметр | Значение (на 2026-08-14) |
|----------|----------|
| Профиль Happ | **Один:** `🇩🇪 Германия` (VLESS TCP Reality JSON) |
| Дверь | `37.46.134.98:8444` (NEW) |
| Двор | Contabo |
| Гибрид Wi‑Fi Vision | **ВЫКЛ** (`VPN_SUBSCRIBE_HYBRID_WIFI_STAGING=false`) |
| Elimination | `all` + `bridge_only` (всем один мост) |
| Vision-flow в Happ JSON | `false` |
| Split | `VPN_SUB_BUNDLE_ROUTING_MODE=ru_direct` ✅ (с 2026-08-02; банки/VK/Ozon direct) |
| WG MTU мост Contabo↔NEW | **1360** (эксперимент 1280 откатили) |
| Staging TID | `493897224` (эксперименты были только на нём; гибрид откатили → как у всех) |

### 14.3 Что тестировали → результат → откат

| # | Эксперимент | Кому | Результат | Откат |
|---|-------------|------|-----------|-------|
| 1 | Staging hybrid: «Домашний Wi‑Fi» Contabo `:443` + мост | только TID `493897224` | Wi‑Fi-direct **плохо / нет интернета** | `HYBRID_WIFI_STAGING=false` |
| 2 | Vision-flow только в Happ (телефон) | hybrid TID | **Не пингуется** | flow flag → false |
| 3 | Порт Wi‑Fi `:8446` (+ фикс: hybrid брал wifi_values) | hybrid TID | **Тоже не работает** | порт/гибрид откат |
| 4 | Flow **с двух сторон** (UUID на Contabo `:443`/`:8446` = vision + Happ flow) | только UUID владельца | **Всё ещё нет интернета** на «Домашний Wi‑Fi» | UUID снова без flow; flag false |
| 5 | MTU WG `1360→1280` Contabo + NEW | **инфра моста (все)** | Германия **так же / хуже** | **MTU 1360** |
| 6 | Имя профиля `🇩🇪 Германия` | всем в `/sub/` | ✅; баг: `bridge_only` хардкодил `🇪🇺` — **исправлено** | — |
| 7 | Split `ru_direct` | уже в проде | LIVE verify: sber/vk/ozon/wb → direct; catch-all → edge-bridge | не трогали |

**Диагностика Contabo при мёртвом Wi‑Fi-direct:** порты `:443`/`:8446` OPEN снаружи, UFW OK, UUID в clients, Reality shortId OK.  
Значит: не «дверь сервера закрыта», а **путь Reality Contabo с домашнего Wi‑Fi владельца не поднимается** (DPI/маршрут). Мост NEW при этом работает.

**Вывод кампании:** идея «Wi‑Fi = 1 hop как Save» на этом ISP/устройстве **не взлетела**. Прод снова = **только мост** (надёжность > скорость Save).

### 14.4 Автозамеры Contabo CF (path-metrics) — разбор «плавает»

| | |
|---|---|
| Cron | каждый час `vpn_path_host_metrics.sh` (Contabo + NEW) |
| CSV | `/var/lib/aladdin-vpn-ops/path_host_metrics.csv` |
| Лог | `/var/log/aladdin-vpn-path-metrics.log` |
| Выборка | Contabo **833** точек (2026-07-23 → 2026-08-14) |
| Медиана CF | ~**10.3 MB/s** |
| «3.0…13.8» в боте | окно последних точек (напр. 14:05Z=3.0 при load1=2.36; 15:05Z=13.8 при load=0.2) |

**Закономерности (простым языком):**

1. **Нагрузка CPU** — главная связь: при load1≥2 медиана CF ~4; при load&lt;0.5 ~13.  
2. Сессии VPN и RTT моста — **слабая** связь.  
3. Вечер MSK чуть хуже дня — **не в разы**.  
4. Один короткий CF-тест раз в час **шумный** (скачки ×3–×5 нормальны).  
5. NEW RU CF спокойнее; фраза бота про «плавает» = **двор Contabo→CF**, не «дверь РФ сломана».

**Не делать:** апгрейд CPU/RAM Contabo «из‑за 3…14»; NL-ноду «потому что бот сказал плавает».  
**Паника:** CF &lt;2 MB/s **несколько часов подряд** или массовый «мёртвый» Happ.

### 14.5 Baseline телефонов (уже есть в сейфе)

Устройство: iPhone SE 2020 · MegaFon VIP. SSOT: `~/ALADDIN_VPN_SAFE/.../BASELINE_SPEEDTEST_20260813-14.md`

| Кто | Сеть | ↓ Mbps (ориентир) |
|-----|------|-------------------|
| Мы (Contabo path / LTE) | LTE | типично вечер ~22–30; утро до ~65 (Contabo↔Contabo смещён) |
| Save | LTE | ~117–125 |
| Save | Wi‑Fi | ~36 / ↑46 |
| Save JSON | — | NL `:443` Vision+flow, 1 hop, split RU; **ключи Save не копировать** |

Сравнивать только LTE↔LTE и Wi‑Fi↔Wi‑Fi.

### 14.6 Почему видео тормозит — независимое резюме (после всех тестов)

Наиболее вероятные причины **сейчас** (прод = только мост):

1. **Двойной hop:** телефон → NEW → WG → Contabo → CDN (лишняя задержка/потери vs Save 1 hop NL).  
2. **Spot Contabo egress** иногда слабый в момент стрима (load + шум канала) — но CF-тест ≠ полный диагноз.  
3. **LTE/DPI/bufferbloat** на стороне клиента (loaded ping в baseline до 800+ ms).  
4. **Peering Contabo ≠ Cherry/NL у Save** — даже при «живом» VPN Mbps до CDN другой.  
5. Прямой Contabo Vision с дома **не вариант** для этого владельца (все варианты FAIL).

### 14.7 Что делать дальше (порядок)

1. **Владелец:** на **🇩🇪 Германия** — Reels + TikTok 30 с (Wi‑Fi и отдельно LTE); записать «буфер / ок».  
2. **Ops:** смотреть `tunnel_speed_timeseries.csv` + path-metrics **вместе** с симптомом «сейчас тормозит».  
3. **Улучшить метрику** (S1): 2–3 CF → медиана; в `/vpn_health` писать load1.  
4. **Не** возвращать hybrid Vision без нового GO и другого ISP-теста.  
5. Если разрыв со Save всё ещё «в разы» на мосту → оценивать **P02 / NL egress** (§7), не CPU Contabo.  
6. UX resilience параллельно: **F02–F04** (если VPN не коннектится).

### 14.8 Запреты этой кампании (повтор)

- Не gRPC «как у Save»; не апгрейд CPU «из‑за 50 юзеров».  
- Не `DIRECT_VISION` / hybrid **всем** без staging.  
- Не merge `VPN_SPEED_DEGRADATION_HANDOFF_RU.md` в этот файл.  
- Не путать cutover entry с экспериментами скорости в одном окне (F08).

---

## 15. Shop Bot — архитектура кассы (Stars/Premium/VPN/реф/розыгрыш)

> **Зачем §15 здесь:** VPN-playbook = «мозг/дверь/двор» + касса. Касса = Telegram Shop Bot.  
> Полный разбор кода: [`telegram_stars_shop_bot/docs/BOT_ARCHITECTURE_REFERENCE_RU.md`](../../../telegram_stars_shop_bot/docs/BOT_ARCHITECTURE_REFERENCE_RU.md).  
> Cursor canvas (живая сводка): `shop-bot-architecture` · розыгрыш: `giveaway-vpn-drop-plan`.

### 15.1 Три процесса + VPN API

| Процесс | Точка входа | Роль | Где |
|---------|-------------|------|-----|
| Telegram bot | `bot/main.py` | UX, заказы, реф, VPN-меню | **Contabo** `185.225.233.150` (единственный poller) |
| Partner API | `partner_api/main.py` `:8090` | Вебхуки оплаты, `/v1`, legal | MAIN + Contabo |
| Webhook worker | `partner_api/webhook_worker.py` | Исходящие события партнёрам | рядом с API |
| VPN API | `aladdin_shop_vpn_api` `:8091` | provision, `.conf`, `vpn.db` | Contabo `/opt/aladdin-shop-vpn-api` |

**Один poller:** на MAIN `aladdin-telegram-bot` **inactive**. Иначе `TelegramConflictError` и разъезд `shop.db`. Канон: `BOT_SINGLE_INSTANCE_CANON.md`.

### 15.2 Продукты

| Продукт | Как работает |
|---------|----------------|
| **Stars / Premium / Gifts** | Витрина `shop.py` ← `products.yaml` → оплата (Ckassa/LAVA/Crypto/xRocket/баланс) → fulfill (iStar/оператор). Статусы: `pending_payment` → `paid` → `processing` → `completed`. |
| **VPN** | Заказ `kind=vpn` в `shop.db` → HMAC `POST /internal/v1/provision` → worker → peer → авто `.conf`/QR. Бот **не** трогает `wg0`. |
| **Partner API** | `X-API-KEY` → заказы/топапы → `outbound_webhook_events`. |

Сквозной поток: `/start ref_<tid>` → онбординг → хаб → покупка → webhook → `completed` → `order_flow.apply_completed_side_effects` (₽-комиссия + VPN-дни).

### 15.3 Рефералка ₽ (кратко)

Канон: `REFERRAL_LEVELS_ANTIBUSE_CANON_2026-07-28.md` · код: `referral_partner.py` + `order_flow._compute_referral_commission`.

| Кошелёк | Поле |
|---------|------|
| Основной | `users.balance_rub` |
| Реферальный | `users.ref_balance_rub` |
| Журнал | `ledger` + `referral_accruals` |

Уровни по друзьям с VPN ≥30д: Старт 15%/1% → Бронза 20%/2% → Серебро 25%/2.5% → Золото 30%/3%.  
Приоритет ставок: personal `ref_partner_rates` → legacy override → уровни.  
Вывод: ≥1000 ₽ · ≥5 друзей VPN≥30д · свой VPN≥30д · cooldown 7д · approve админом.

### 15.4 Базы данных

| БД | Путь | SSOT |
|----|------|------|
| `shop.db` | `/opt/aladdin-telegram-shop-bot/data/shop.db` | **Contabo** (заказы, юзеры, реф, giveaway) |
| `vpn.db` | `/opt/aladdin-shop-vpn-api/var/vpn.db` | VPN API host |
| Backend iOS DBs | `/opt/aladdin-backend/...` | **Не** shop-bot |

Ключевые таблицы `shop.db`: `users`, `orders`, `ledger`, `referral_*`, `vpn_referral_*`, `partner_contests` (старый топ по заказам), **`giveaway_*`** (новый VPN Drop), `api_clients`, `payment_provider_events`, …

### 15.5 Карта кода бота

| Зона | Путь |
|------|------|
| Handlers | `bot/handlers/{common,hub,shop,vpn,admin}.py` |
| Схема БД | `bot/db/database.py` |
| Начисления ₽ | `bot/services/order_flow.py` |
| Уровни/вывод | `bot/services/referral_partner.py` |
| Старый конкурс | `bot/services/contest_repo.py` (`partner_contests`) |
| VPN Drop | `bot/services/giveaway_*.py` |
| Каталог | `bot/products.yaml` |
| Partner API | `partner_api/routers/*` |
| Деплой бота | `docs/ML_SYSTEM_HANDOFF_FINAL.md` |

### 15.6 VPN Drop (розыгрыш билетов) — статус

Полный план: [`PLAN_GIVEAWAY_VPN_DROP_2026-08-15.md`](../../../telegram_stars_shop_bot/docs/PLAN_GIVEAWAY_VPN_DROP_2026-08-15.md).

| | |
|---|---|
| Модель | Билеты за действия **без** регистрации; **без** публичного лидерборда |
| Срок / сток | 7 дней · 50 призов (3×12м + 7×6м + 10×3м + 30×30д) |
| Билеты | канал +1 · ref start +2 · trial +5 · VPN purchase +10 · cap 100 реф |
| Draw | Random по билетам · 1 приз/человек |
| Канал | Если победитель **отписан** → приз не выдаём · **реролл только этого места** (`gvd-32b`) |
| TODO | `gvd-*` в Cursor · схема `giveaway_*` уже в миграциях |

**Не путать** с `partner_contests` (старый топ по completed-заказам рефералов).

### 15.7 Связь с VPN data-plane (этот playbook)

| Касса (бот) | Data-plane (этот файл §0–§14, §16) |
|-------------|-------------------------------|
| Оплата / заказ / билеты розыгрыша | Entry / egress / Happ+Incy `/sub/` |
| `shop.db` Contabo | `vpn.db` Contabo |
| Приз VPN Drop → `post_add_subscription_days` / provision | Тот же VPN API, что после оплаты |
| Кнопки Incy / self-reset (§16) | HWID gate + `device_limit` на Contabo |

`VPN_SPEED_DEGRADATION_HANDOFF_RU.md` — **только ссылка** в карте выше; **не** merge сюда (§32 secrets).

Оплата СБП/карта LAVA (H2H ↔ classic) — **§17**, полный файл в `telegram_stars_shop_bot/docs/`.

### 15.8 Бот молчит на `/start` — Telegram Bot API soft-block + рот Mouth (prod)

> Инциденты soft-block: 2026-07-13/14 и **2026-08-18**. Симптом: сайт Telegram живой, фейковый токен → 401, **настоящий getMe висит**. Не баг меню.  
> **Прод с 2026-08-27 (`ops-01`):** Bot API egress ≠ VPN egress. Бот на Brain ходит в `api.telegram.org` **через Mouth**.

**SSOT soft-block:** [`telegram_stars_shop_bot/docs/ML_SYSTEM_HANDOFF_TELEGRAM_BOTAPI_SOFTBLOCK.md`](../../../telegram_stars_shop_bot/docs/ML_SYSTEM_HANDOFF_TELEGRAM_BOTAPI_SOFTBLOCK.md)  
**Шаги рта:** [`BOT_TELEGRAM_API_EGRESS_ML_HANDOFF_2026-07-14.md`](../../../telegram_stars_shop_bot/docs/BOT_TELEGRAM_API_EGRESS_ML_HANDOFF_2026-07-14.md) §4  
**Метрики P1:** `~/ALADDIN_VPN_SAFE/bot_rot_metrics_20260827.md`  
На Contabo: `/opt/aladdin-telegram-shop-bot/shared/ml/`

#### Схема (прод)

```text
VPN-клиенты  → NEW :8444 → WG → Brain egress     (как было)
Бот AiMonkey → Brain process → SOCKS Mouth:1080 → api.telegram.org
                 (TELEGRAM_PROXY_URL в shared/.env)
```

| Компонент | Где | Факт |
|-----------|-----|------|
| Бот / `shop.db` / касса / vpn-api | Brain `185.225.233.150` | **Не переезжали** |
| SOCKS5 | Mouth `169.58.242.12:1080` | **3proxy** (unit `bot-mouth-3proxy`); UFW: порт только с Brain |
| Env | Brain `/opt/aladdin-telegram-shop-bot/shared/.env` | `TELEGRAM_PROXY_URL=socks5://…@169.58.242.12:1080` |
| Код | `bot/main.py` + `bot/config.py` | `AiohttpSession(proxy=…, timeout=180)` · venv: `aiohttp-socks` |
| Scope | **Все** пользователи бота | Не staging-TID (в отличие от P2 VPN bundle) |
| microsocks | — | ❌ снят: long-poll timeout/reset; **не возвращать** без GO |

#### Откат на прежнюю схему (≤2 мин) — «убрать одну строку»

```bash
# Brain — не печатать токен/пароль в чат
ENV=/opt/aladdin-telegram-shop-bot/shared/.env
cp -a "$ENV" "${ENV}.bak-rollback-$(date +%Y%m%d-%H%M%S)"
grep -v '^TELEGRAM_PROXY_URL=' "$ENV" > /tmp/env.noproxy && cat /tmp/env.noproxy > "$ENV" && chmod 600 "$ENV"
systemctl restart aladdin-telegram-bot
# Окно: 1–2 мин бот может не отвечать, пока поднимается polling
systemctl is-active aladdin-telegram-bot
# PASS: /start у @AiMonkeyStars_bot; getMe с Brain напрямую 200
```

Откат **не** требует гасить Mouth. VPN/Lava/`shop.db` не трогать.

#### Как чинить (если снова молчит)

| # | Проверка | Действие |
|---|----------|----------|
| 1 | `systemctl is-active aladdin-telegram-bot` + `bot-mouth-3proxy` | Restart упавшего unit |
| 2 | Лог: `TelegramNetworkError` / нет `Update id=` | Смотреть Brain↔Mouth `ss` на `:1080` |
| 3 | getMe **через** SOCKS с Brain vs **напрямую** с Brain / с Mouth | Если SOCKS плохой → откат §выше; если Mouth direct плохой → soft-block на IP рта |
| 4 | После релиза бота пропал proxy | Вернуть `TELEGRAM_PROXY_URL` + убедиться `aiohttp-socks` в venv |
| 5 | Долго молчит / неизвестно | **Откат** (строка env) → стабилизировать → разбор отдельно |

| Делать | Не делать |
|--------|-----------|
| Прозвон getMe (токен не в чат) | Второй poller на MAIN |
| Откат proxy одной строкой | Restart-storm; `getUpdates` при живом poller |
| Касса/VPN API не трогать «на всякий» | Бесплатный публичный SOCKS; рот через RU-дверь; перенос `shop.db` |
| Предпочитать **socks5://** (не socks5h — был timeout) | Возврат microsocks без GO |

#### Автоfailover «A-owner» (prod ✅ 2026-08-27)

| Параметр | Значение |
|----------|----------|
| Timer | `bot-mouth-autofailover.timer` каждые **5 мин** |
| Скрипт | `/usr/local/sbin/bot-mouth-autofailover.sh` (репо: `telegram_stars_shop_bot/scripts/bot_mouth_autofailover.sh`) |
| State | `/var/lib/aladdin-bot-mouth-autofailover/state` |
| Триггер | **5 FAIL подряд** (~25 мин) **или** **5 медленных** подряд (каждый getMe через proxy **t > 60 с**, ~25 мин) |
| Действие | убрать `TELEGRAM_PROXY_URL`, поставить `TELEGRAM_PROXY_AUTO_DISABLED=1`, restart бота, алерт в `ALERT_TELEGRAM_*` (**напрямую**, не через Mouth) |
| Если direct getMe тоже FAIL | **не** трогать proxy — только алерт «Telegram/Brain» |
| Обратно на Mouth | **только вручную** (убрать `TELEGRAM_PROXY_AUTO_DISABLED`, вернуть `TELEGRAM_PROXY_URL`, restart) |

Ужесточение позже (без смены логики): interval 2 мин / 3 FAIL — правки `OnUnitActiveSec` + `FAIL_NEED` в скрипте/timer.

**Следующий апгрейд рта (если Contabo Mouth тоже soft-block):** отдельный **non-Contabo** mini-VPS только SOCKS — по фразе владельца.

### 15.9 Бот молчит на VPN-кнопках — `display_seq` / DB lock / `NameError` (не soft-block)

> **Инцидент 2026-09-04.** Симптом: webhook/`getMe` **живые**, `/start` иногда отвечает, но **VPN / тарифы «молчат»**.  
> Класс **другой**, чем §15.8 (там getMe висит).

**SSOT:** [`telegram_stars_shop_bot/docs/ML_SYSTEM_HANDOFF_BOT_SILENT_DISPLAY_SEQ_LOCK_2026-09-04.md`](../../../telegram_stars_shop_bot/docs/ML_SYSTEM_HANDOFF_BOT_SILENT_DISPLAY_SEQ_LOCK_2026-09-04.md)  
**Ops-memory:** `docs/ops-memory/incidents/2026-09-04__bot_silent__display_seq_lock.md`

#### Цепочка (простыми словами)

```text
заказ без display_seq (NULL)
  → фоновые connect() гоняют migrate/backfill
    → UNIQUE display_seq / write-lock на shop.db
      → analytics падает → NameError: logger (было) → callback умирает → кнопка молчит
```

#### Что уже сделано (Mac + Contabo 2026-09-04)

| Мера | Зачем |
|------|--------|
| Stamp `display_seq` во всех `create_*` (в т.ч. balance) | NULL больше не рождается |
| `connect(..., run_migrations=False)` default | migrate только на boot бота |
| Safe backfill (без full reshuffle) | не ломает UNIQUE mid-txn |
| `log_event` fail-soft | аналитика не валит UX |
| Watchdog: lock / NameError / NULL seq | алерт до жалоб |

#### Быстрая triage (2 мин на Brain)

```bash
systemctl is-active aladdin-telegram-bot
# getMe живой? (токен не в чат) — если висит → §15.8, не этот раздел
tail -n 200 /opt/aladdin-telegram-shop-bot/logs/bot.log | \
  grep -E 'NameError|database is locked|display_seq|callback_timing|db_migrate'
sqlite3 /opt/aladdin-telegram-shop-bot/data/shop.db \
  "SELECT COUNT(*) FROM orders WHERE display_seq IS NULL;"
# PASS: 0 · скрипт: current_app/scripts/check_shop_db_display_seq.sh
```

| Наблюдение | Класс | Куда |
|------------|-------|------|
| getMe timeout | soft-block | §15.8 |
| `NameError` / `locked` / `UNIQUE display_seq` | этот | handoff §6 |
| NULL count > 0 | регресс create-path | P0 stamp · handoff |

---

## 16. Incy + Happ: клиенты, HWID, слоты 3 админов (2026-08-16)

**Для другой ML-системы:** это **не** два VPN-протокола и **не** две ссылки.  
Это **два клиента** (приложения) к **одной** подписке `/sub/` и **одному** протоколу data-plane (**VLESS Reality** через дверь NEW).

Полный план/TODO: `telegram_stars_shop_bot/docs/PLAN_INCY_SUPRA_LIGHT_STAGING_2026-08-16.md` · ids `incy-a-*`.

### 16.1 Что было → что стало

| | Было | Стало (прод 2026-08-16) |
|--|------|-------------------------|
| Клиент | Практически только **Happ** | **Happ** (мир) + **Incy** (РФ App Store) |
| `/sub/` HWID-гейт | UA без `happ` → stub «App not supported» | Happ как раньше; **Incy** разрешён при `VPN_SUB_INCY_CLIENT_MODE=all` |
| Ссылка / opaque / UUID / оплата | — | **Не меняли** (ни массовой миграции) |
| Устройства (канон) | лимит 1 у большинства | **Вариант B:** лимит **1** у обычных; Happ↔Incy = **сброс** (не поднимали дефолт до 2) |
| UX бота | Open/Download Happ | + Open/Download Incy; self-service сброс в «⚙️ Настройки» |
| Приветствие хаба | без клиентов | строка: `📱 VPN-клиент на выбор: Happ — мир · Incy — РФ (одна ссылка)` (`bot/ui_copy.py`) |

### 16.2 Как устроено (архитектура для ML)

```text
Телефон: Happ ──┐
                ├──► HTTPS /sub/<opaque>  (мозг Contabo :8091 / публичный домен)
Телефон: Incy ──┘         │
                          ├─ HWID gate (sub_hwid_gate.py)
                          ├─ device_limit / vpn_device_bindings
                          └─ VLESS Reality JSON → дверь NEW :8444 → egress Contabo
```

| Компонент | Где | Что править |
|-----------|-----|-------------|
| Incy whitelist | Contabo `/opt/aladdin-shop-vpn-api` | `sub_hwid_gate.py`, `settings.py`, env `VPN_SUB_INCY_CLIENT_MODE` / `VPN_SUB_INCY_CLIENT_STAGING_TIDS` |
| Deep link bridge | Partner API Contabo (+ MAIN sync) | `partner_api/routers/incy_open_bridge.py` → `incy://add/…` · Happ: `happ_open_bridge.py` |
| Кнопки бота | Contabo shop-bot | `vpn_post_purchase_delivery.py`, `handlers/vpn.py`, `vpn_devices_platform_hub.py` |
| Self-reset | bot → vpn-api | `vpn_device_reset_self.py` · API `POST /internal/v1/device_reset` + `actor_telegram_user_id` при `reason=user_self_service` |
| Константы магазинов | бот | `vpn_happ_constants.py`, `vpn_incy_constants.py` |

**Env (vpn-api Contabo, без секретов в git):**

| Ключ | Прод сейчас | Смысл |
|------|-------------|--------|
| `VPN_SUB_INCY_CLIENT_MODE` | **`all`** | Incy для всех активных `/sub/` (не только owner) |
| `VPN_SUB_INCY_CLIENT_STAGING_TIDS` | `493897224` (список) | Используется только при `MODE=staging` |

**Откат Incy:** только по фразе владельца **`ROLLBACK INCY`**.  
Бэкапы: `~/ALADDIN_VPN_SAFE/incy_supra_light_prebackup_20260816-124457/` · deploy `~/ALADDIN_VPN_SAFE/incy_a36_deploy_20260816-153800/`.

### 16.3 HWID — правило для поддержки и ML

1. HWID = отпечаток телефона/клиента.  
2. Первый клиент, обновивший `/sub/` с HWID, **занимает слот**.  
3. **Happ и Incy = разные HWID** → при `device_limit=1` одновременно **нельзя**.  
4. Сброс чистит `vpn_device_bindings` (+ HWID в slots) **только своего** TID; opaque/оплату не трогает.  
5. После сброса: обновить подписку **только в одном** приложении.

**Self-reset (user):** callback `vpn:hwid_reset:ask|yes|no` — **без TID в data**; `tid = from_user.id`; rate-limit ~15 мин; audit `vpn_self_device_reset_audit`.  
**Self-reset (web SPA, UX3 2026-08-26):** `POST /v1/web/devices/reset-hwid` — тот же `device_reset` + cooldown ~15 мин; **revoke одного** устройства (`/web/devices/revoke`) остаётся отдельно.  
**Admin reset:** `/admin_vpn_device_reset <tid>` — отдельно, может чужих.

### 16.3a UX3 — 2 слота новым + get_capacity из БД (2026-08-26)

| Правило | Значение |
|---------|----------|
| `VPN_DEVICE_LIMIT_DEFAULT` | **2** (Contabo `env` + код) |
| Новые trial/paid | INSERT `device_limit=2` |
| Старые с `device_limit=1` | **не** backfill |
| `get_capacity()` | ceiling = `device_limit` из `vpn_accounts` (не hard-cap 1) |
| Trial квота | **10 GiB** без изменений |
| Ops-исключения | вручную 3/5 (админы; ShellGrinder=3) — как раньше |

План: `telegram_stars_shop_bot/docs/PLAN_UX3_TRAF_WIZARD_TWO_SLOTS_WEB_RESET_2026-08-26.md`.

### 16.4 Три админа — кто есть кто и слоты (канон, проверено 2026-08-16)

**Правило:** у каждого человека **один** @username и **один** номер TID.  
Не писать «@A / @B» на один номер — это путаница.

#### Соответствие (Contabo `shop.db`)

| Кто | Номер (TID) | Имя в БД |
|-----|-------------|----------|
| **@Sergey210284** | **493897224** | Sergey |
| **@Mishabakh** | **744254201** | Миша |
| **@dmitriy777vne** | **854726070** | Dmitriy |

Эти же три TID в `ADMIN_IDS` / `SUPER_ADMIN_IDS` на Contabo.

#### Результат (как есть сейчас) — Contabo `vpn.db`

| Кто | Номер (TID) | Сколько устройств можно | Уже занято телефонами | Свободно |
|-----|-------------|-------------------------|------------------------|----------|
| **@Sergey210284** | **493897224** | **5** | 4 | **1** |
| **@Mishabakh** | **744254201** | **5** | 1 | **4** |
| **@dmitriy777vne** | **854726070** | **5** | 2 | **3** |

Смысл колонок: **можно** = `device_limit`; **занято** = число HWID в `vpn_device_bindings`; **свободно** = можно − занято.

#### Что сделали ops (2026-08-16)

| Кто | TID | Было (лимит) | Стало | Что изменили |
|-----|-----|--------------|-------|--------------|
| @Sergey210284 | 493897224 | 5 | 5 | **не трогали** (уже было 5) |
| @Mishabakh | 744254201 | 1 | **5** | подняли потолок (+4 свободных места) |
| @dmitriy777vne | 854726070 | 2 | **5** | подняли потолок (+3 свободных места) |

**Сделали:** только `UPDATE vpn_accounts SET device_limit=5` для этих трёх TID.  
**Не сделали:** не трогали обычных пользователей; не удаляли и не переносили чужие HWID; не «забирали» слоты у других.

**Не путать:** с **2026-08-26 (UX3)** новым клиентам по умолчанию **лимит 2**; у кого в БД уже `1` — остаётся `1` (без backfill). Админские **5** — исключение для ops.

Проверка:

```bash
# на Contabo — лимиты
sqlite3 /opt/aladdin-shop-vpn-api/var/vpn.db \
  "SELECT telegram_user_id, device_limit,
          (SELECT COUNT(*) FROM vpn_device_bindings b
           WHERE b.telegram_user_id=a.telegram_user_id) AS bindings
   FROM vpn_accounts a
   WHERE telegram_user_id IN (493897224,744254201,854726070);"

# username ↔ TID
sqlite3 /opt/aladdin-telegram-shop-bot/data/shop.db \
  "SELECT user_id, username, first_name FROM users
   WHERE user_id IN (493897224,744254201,854726070);"
```

### 16.5 Что нажимать в боте (шпаргалка для людей)

1. **🌐 VPN** → **Открыть в Happ / Incy** или **Скачать Happ / Incy**.  
2. Смена телефона или Happ↔Incy: **⚙️ Настройки → 📱 Сброс устройства → ✅**.  
3. Обновить подписку **в одном** клиенте.  
4. «Лимит устройств»: **⚙️ Настройки → ❓ Если лимит устройств** (канон-текст ниже) → Сброс.

**Канон-текст «лимит» (вариант 3):**  
«Видите „лимит устройств“? Это не ошибка оплаты. Слот занят.  
Освободите: ⚙️ Настройки → Сброс → одно приложение (Happ или Incy на выбор) → обновить 🔄.»

**Гигиена:** ссылку никому не слать; не поднимать всем `device_limit=2` без GO; квартальный SQL «дубли opaque=0».

### 16.6 Если нужно что-то поменять (чеклист ML)

| Задача | Куда | Осторожно |
|--------|------|-----------|
| Выключить Incy для всех | Contabo env `VPN_SUB_INCY_CLIENT_MODE=off` → restart `aladdin-shop-vpn-api` | Happ не ломается |
| Снова только owner | `MODE=staging` + TID в `VPN_SUB_INCY_CLIENT_STAGING_TIDS` | |
| Поднять лимит юзеру | SQL/`device_limit` на Contabo `vpn.db` | Не путать с bindings |
| Сбросить HWID юзеру | admin cmd или user self-reset | Не трогать opaque |
| Кнопки / тексты | Contabo bot release + restart poller | MAIN bot **inactive** (маркер `SHOP_BOT_POLLING_HOST` только Contabo) |
| Deep link Incy | partner_api `open-incy` | Публично: `https://aimonkeystars.ru/v1/vpn/open-incy` |

**Деплой bot (канон):** Contabo poller + MAIN sync без второго poller — `telegram_stars_shop_bot/scripts/deploy_prod.sh` / `verify_single_bot.sh`.

---

## 17. Касса LAVA: H2H ↔ classic — как устроено и как переключать

> **Полный playbook для другой ML-системы (канон оплаты):**  
> [`telegram_stars_shop_bot/docs/ML_SYSTEM_HANDOFF_PAYMENTS_LAVA_H2H_CLASSIC_2026-08-17.md`](../../telegram_stars_shop_bot/docs/ML_SYSTEM_HANDOFF_PAYMENTS_LAVA_H2H_CLASSIC_2026-08-17.md)  
> Зеркало сейфа: `~/ALADDIN_VPN_SAFE/ENTRY_CLONE_KIT/PAYMENTS_LAVA_H2H_CLASSIC_PLAYBOOK_RU.md`  
> История пилота: `HANDOFF_LAVA_H2H_PILOT_NEXT_ML_2026-08-17.md`.  
> **Не** склеивать с `VPN_SPEED_DEGRADATION_HANDOFF_RU.md`.

Касса **отдельно** от двери VPN. Не в одном окне с cutover entry / сменой egress.

### 17.1 Простыми словами

LAVA на **одной** кассе: либо H2H СБП, либо обычная форма. Поэтому две кассы:

| Касса | Для чего |
|-------|----------|
| **65fb** | СБП H2H: наша страница + QR `qr.nspk.ru` |
| **a817** | Карта + запасной СБП. **Не** включать H2H-тариф здесь (ломало оплату 2026-08-14) |

| Кнопка | Сейчас |
|--------|--------|
| Сайт СБП | QR НСПК на aimonkeystars |
| Сайт карта | LAVA a817 |
| Бот СБП | `/pay/b/{token}` (наша страница) |
| Бот карта | сразу LAVA a817, без `/pay/b/` |

После оплаты Happ-ссылки: в **бот** если есть Telegram, и на **сайт** `/o/…`.

### 17.2 Быстрый рычаг (безопасно)

**Да, переключаем за минуты.** Только флаг, **не** кабинет LAVA.

| Режим | Env на Contabo `shared/.env` | Restart |
|-------|------------------------------|---------|
| H2H СБП (прод 2026-08-17) | `LAVA_H2H_SBP_ENABLED=1` | **только** `aladdin-partner-api` |
| Классика СБП (форма LAVA) | `LAVA_H2H_SBP_ENABLED=0` | **только** `aladdin-partner-api` |

Карта **не** зависит от флага (всегда a817). Бот рестартовать не нужно. Ключи 65fb не удалять. `LAVA_H2H_FALLBACK_INVOICE=1` оставить.

Смоук: `curl -sS http://127.0.0.1:8090/v1/web/health` → `lava_h2h_sbp_enabled` true/false.  
Сайт: H2H=1 → QR НСПК (или fallback a817); H2H=0 → `pay.lava.ru`.  
Бот: СБП = aimonkeystars `/pay/b/`; Карта = lava-open.

Команды и запреты — в полном playbook §5–§6.

### 17.3 Запреты (касса)

- H2H-тариф на **a817**  
- Номер карты / CVV на наш сервер (PCI)  
- Второй poller бота на MAIN  
- Секреты `.env` и VPN-handoff §32 в git/чат  

---

**Конец главного файла VPN.**  
Править статусы здесь; краткий backlog-зеркало — в `VPN_RESILIENCE_MINPLAN_RU.md` (со ссылкой сюда).  
Скорость видео / hybrid — **§14**.  
Shop Bot (касса / реф / розыгрыш) — **§15** + полные MD в `telegram_stars_shop_bot/docs/`.  
**Incy / Happ / HWID / админ-слоты — §16.**  
**Оплата LAVA H2H ↔ classic — §17** (полный файл: `ML_SYSTEM_HANDOFF_PAYMENTS_LAVA_H2H_CLASSIC_2026-08-17.md`).  
Следующие шаги владельца: Happ Reels/TT на 🇩🇪 + `/vpn_health`. UX агента по GO: F02+F03.


## 18. P2 Bundle 10 профилей — Asia-via-NEW (канон 2026-08-27)

> **Ничего из §0–§17 не удалялось.** Этот раздел фиксирует сделанное и прод-архитектуру после owner PASS 10/10.

### 18.1 Что сделали (хронология)

| Шаг | Факт |
|-----|------|
| T1 bak | `PRE_P2_T1_20260827-125539` (сейф) |
| Mouth rot | Bot API SOCKS Mouth `…12` ✅ (не VPN) |
| `jam-70` | WG Brain↔SG `10.10.0.4` + SG Reality `:443` |
| `jam-31/32` | код 10-prof + unit tests; `MULTI_COUNTRY_MODE=staging` + TID `493897224` |
| Reality Asia direct | Contabo dest/SNI → `www.cloudflare.com`; e2e с серверов PASS, **с телефона РФ — отвал** |
| Reality EU | все EU SNI → `max.ru` (согласовано с NEW dest) |
| **Asia-via-NEW** | NEW inbound `asia-bridge-in` **`:8445`** → outbound `sg-hop` → SG `:443`; hop-UUID на SG |
| `/sub/` Asia | `VPN_SG_PUBLIC_HOST=37.46.134.98` `VPN_SG_PORT=8445` + **bridge** Reality keys; `VPN_SG_DIRECT_*` = ключи hop на SG |
| Owner drill | **10/10 профилей работают** (владелец 2026-08-27) |
| `jam-34` | ✅ **применено** `VPN_SUBSCRIBE_MULTI_COUNTRY_MODE=all` · smoke 5 TID · e2e PASS · пользователям обновить `/sub/` |

### 18.2 Архитектура (прод)

| Профили | Адрес в `/sub/` | Порт | Reality | Exit IP |
|---------|-----------------|------|---------|---------|
| 🇩🇪🇳🇱🇫🇮🇵🇱🇸🇪 | NEW `37.46.134.98` | **8444** | bridge (`max.ru`, sid `b1c2d3e4`) | Brain `185.225.233.150` |
| 🇸🇬🇯🇵🇰🇷🇭🇰🇹🇭 | NEW `37.46.134.98` | **8445** | **те же** bridge keys | SG `217.15.166.78` |

**Env (Brain `/opt/aladdin-shop-vpn-api/env`):**

- `VPN_SUBSCRIBE_MULTI_COUNTRY_MODE=all` (после jam-34; было `staging`)
- `VPN_ASIA_ENTRY_MODE=via_new` · `VPN_ASIA_ENTRY_PORT=8445`
- `VPN_SG_*` = client-facing Asia entry (NEW)
- `VPN_SG_DIRECT_*` = SG Reality для hop (ops only)
- Meta: `/opt/aladdin-shop-vpn-api/var/asia-bridge-hop.json` · сейф `~/ALADDIN_VPN_SAFE/asia-bridge-hop.json`

**NEW `/opt/xray-bridge/config.json`:** tags `ru-bridge-in` `:8444` → `contabo-hop`; `asia-bridge-in` `:8445` → `sg-hop`.

**SG `/opt/xray/config.json`:** `:443` Reality + hop-UUID (+ user UUIDs могут оставаться для rollback).

### 18.3 Алгоритм выката всем (jam-34) — повторить 1:1

1. Owner PASS 10/10 (уже).  
2. Bak env: `cp env env.bak.jam34_$(date +%Y%m%d-%H%M%S)`.  
3. `VPN_SUBSCRIBE_MULTI_COUNTRY_MODE=all` (staging TID можно оставить).  
4. `systemctl restart aladdin-shop-vpn-api`.  
5. Smoke: ≥2 чужих `vpn_active` → JSON **10** профилей; Asia host=`37…` port=`8445`; EU `:8444`.  
6. E2E socks: Asia exit=`217…78`, EU exit=`185…150`.  
7. Канал/бот: «обновите подписку в Happ/Incy».  
8. Rollback: `MODE=staging` + только owner TID.

### 18.4 Что говорить пользователям

> Обновите подписку AiMonkey в Happ или Incy (потяните список серверов / «обновить»).  
> Появятся **10 серверов**: Европа (🇩🇪…) и Азия (🇸🇬…).  
> Если Азия «не пингует» — сначала обновите подписку; вход идёт через ту же дверь Германия, выход — Сингапур.

### 18.5 Связанные файлы

| Файл | Роль |
|------|------|
| `VPN_JAMMING_THREE_WAY_…2026-08-26.md` §1.2 | Канон стран / портов |
| `VPN_JAMMING_…2026-08-20.md` §20 | Журнал выяснений + jam-34 |
| `SERVERS_ACCESS_CANON.md` §9 | SSH/роли после P2 |
| `.cursor/VPN_JAMMING_TASK_REGISTRY.md` | TODO ids |

**Speed handoff:** только ссылка — `VPN_SPEED_DEGRADATION_HANDOFF_RU.md` (§32 не merge).


### 18.6 GOLDEN snapshot (сейф Mac)

`~/ALADDIN_VPN_SAFE/GOLDEN_P2_ASIA_VIA_NEW_LATEST` — env Brain + xray NEW/SG + 3 канона + `ARCHITECTURE_GOLDEN.md`. Не в git.

### 18.7 После P2 (2026-08-27) — уже на проде, не в GOLDEN env-снимке

| ID | Что | Где читать |
|----|-----|-----------|
| `jam-45` | LTE `:5443` всем | registry · three-way §8 |
| `jam-60…62` | TCP probe + `/vpn_health` Entry ≠ CF + алерт двери | handoff §3.3 |
| `fro-03/04` | сайт `aimonkeystars.ru` + support бот · expired **200** stub | handoff §3.4 |
| `jam-52` | запасная кнопка `aladdin-ai.ru/sub/` | ✅ Brain `jam52-…` |
| Next (после 2026-08-28 LTE-ночи) | **не** GO all jam-40 · приоритет **P9 `:443` + другой ASN** · CDN по GO · optional phone MAIN `…180` | §18.8 · registry |

### 18.8 Инцидент 2026-08-28 — ночь: Wi‑Fi OK / LTE всё timeout (для следующей ML)

> **Ничего не удаляли выше.** Это дополнение статистики + сходимость с планом глушилок.

#### Факты (владелец, staging TID `493897224`, ночь ~02:xx MSK / UTC+4)

| Путь | Результат |
|------|-----------|
| **Wi‑Fi** | Работает (🇪🇺 после jam-40 staging — разные SNI) |
| **LTE** | **Не работает ничего:** все 🇪🇺 + профиль **`🇷🇺 LTE` (`:5443`)** → **timeout** |
| Сервер в ту же ночь (read-only) | NEW `:8444/:8445/:5443` **open** с не-мобильного пути · `entry_tcp_probe` **all_ok** · xray-bridge **active** |

#### jam-40 на момент инцидента (staging only — не GO all)

| Шаг | Факт |
|-----|------|
| NEW `:8444` `serverNames` | ~~`vk.com`~~ **убран 2026-08-28** · сейчас: `max.ru`, `yandex.ru`, `www.cloudflare.com`, `www.yandex.ru` |
| Brain | `VPN_EU_SNI_POOL_MODE=staging` · TID `493897224` · остальные EU всё ещё `max.ru` |
| Smoke `/sub/` | staging: DE/NL/FI/PL/SE = разные SNI ✅ · другой TID: все EU `max.ru` ✅ |
| Откат | `VPN_EU_SNI_POOL_MODE=off` + при необходимости `serverNames=[max.ru]` |

#### Гипотезы (статус после уточнения владельца)

| Гипотеза | Статус |
|----------|--------|
| «Плохой» SNI (yandex/vk/cloudflare) | **снята** — даже `max.ru` и perekrestok мертвы на LTE |
| Режут только `:8444` | **ослаблена** — `:5443` тоже timeout |
| Бан / дроп всего IP **`37.46.134.98`** с LTE (или всех non-443 на нём) | **главная** |
| Падение сервера / xray | **нет** — Wi‑Fi на тех же профилях ок |

**Итого одной фразой:** ночной мобильный путь **не доходит TCP до NEW (`…98`)**. Happ крутит handshake → timeout. Домашний Wi‑Fi до того же IP ещё ходит.

#### Как сходится с нашим планом (не новый план — подтверждение старого)

| Уже в плане | Почему ночь это подтверждает |
|-------------|------------------------------|
| §5.H H1/H2 / P9 `jam-20…24` — вторая дверь **`:443`**, другой ASN (не Contabo Vision всем) | Единственный устойчивый обход IP-бана NEW |
| Dendi почти весь на `:443` + много IP | Мы на одном `…98` + non-443 → SPOF ночью на LTE |
| jam-40 multi-SNI «постепенно» | Полезно как дневное разнообразие / A/B; **не** антидот ночного LTE |
| jam-45 `:5443` perekrestok | Другой порт+SNI; **не** спас эту ночь → значит не «только 8444» |
| CDN `jam-50/51` | Чинит `/sub/`, **не** data-plane до двери |
| Не делать H13 («лучше Reality на том же IP») | Подтверждено: крутить SNI на `…98:8444` против этой ночи бессмысленно |

#### Наилучший следующий шаг для ML (порядок)

1. **Не** включать `VPN_EU_SNI_POOL_MODE=all` как ответ на глушилку.  
2. Optional (без деплоя): владелец на LTE проверить **другую дверь** MAIN `…180:8444` (если профиль ещё есть) — отличить «бан только NEW» vs «весь зарубежный VPS».  
3. **P9:** купить/поднять VPS (приоритет RU-friendly ASN) · Reality **`:443`** · staging TID · drill **Wi‑Fi+LTE ночью** · затем GO.  
4. UX: announce «при глушилках переключи Обход / LTE» (`fro-01/02`, `jam-13`) — после появления второй двери.  
5. CDN — отдельный GO, не вместо P9.

**Канон #2 (детали гипотез):** `VPN_JAMMING_DENDI_VS_AIMONKEY_…2026-08-20.md` §0.2 · §5.H.1 · §11.  
**Канон #3 (SSH/роли):** `~/ALADDIN_VPN_SAFE/ENTRY_CLONE_KIT/SERVERS_ACCESS_CANON.md` §9.6 журнал.  
**Registry Next:** `.cursor/VPN_JAMMING_TASK_REGISTRY.md`.

---

## 19. Глушилки LTE — негативные тесты 2026-08-28 (не повторять)

**Для ML:** полный handoff с очередью задач → `ML_SYSTEM_HANDOFF_JAMMING_LTE_NEGATIVE_TESTS_2026-08-28.md`.  
**Краткий инцидент ночи:** §18.8. **§32 secrets:** только ссылка на `VPN_SPEED_DEGRADATION_HANDOFF_RU.md` — **не merge**.

### 19.1 Что выяснили (итог одной строкой)

**Wi‑Fi доказывает, что сервер жив; LTE режет путь до FirstVDS-дверей (NEW `…98` и MAIN `…180`), включая `:443` на Аладдине — нужна P9-дверь на другом ASN, а не ещё SNI/порт на том же хостере.**

### 19.2 Таблица экспериментов — не повторять

| # | Эксперимент | Wi‑Fi | LTE | Вердикт |
|---|-------------|-------|-----|---------|
| 1 | **jam-40** multi-SNI на NEW `:8444` (staging TID) | OK | **FAIL** все SNI + `:5443` | **Не GO all** |
| 2 | **MAIN443** SNI-split `149.154.65.180:443` (staging) | OK | **FAIL** | **Откат DONE** · не повторять на FVDS |
| 3 | jam-45 `:5443` | (днём ок) | **FAIL** ночью | Не LTE-fix alone |
| 4 | CDN `/sub/` | — | — | Не data-plane |
| 5 | Contabo Vision всем | FAIL (§14) | — | Запрещено |

**Rollback MAIN443:** `/opt/xray-bridge/rollback_main443_sni_split.sh` · runbook `deploy/runbooks/MAIN443_SNI_SPLIT_STAGING_2026-08-28.md` · Brain `VPN_SUBSCRIBE_MAIN443_MODE=off`.

### 19.3 jam-20 — чек-лист выбора хостера (P9)

> Не «самый дешёвый VPS», а **другая улица (ASN)** + **:443**.

| Критерий | Да | Нет |
|----------|----|-----|
| **ASN** | ≠ FirstVDS / ≠ **AS29182** | Ещё FVDS / «белый клон» |
| **Порт** | **:443** Reality с первого дня | Только 8444/5443 |
| **Роль** | Дверь → WG → Brain | Contabo Vision всем / новый мозг |
| **SNI** | max / yandex / cloudflare (A/B) | **`vk.com`** · Apple без Apple ASN |
| **Тест** | Staging TID `493897224` · Wi‑Fi + **LTE ночь** | Сразу всем |
| **Запас** | План 2-й ASN через ~месяц | Одна дверь навсегда |

**Приоритет ASN (как Dendi/Frosty):** Yandex Cloud **AS200350** → REG.RU/Selectel **AS197695** → Citytelecom **AS3175**.  
**Избегать:** Hetzner/DO «как все», Contabo как дверь, любой FirstVDS.

**Форумы + опыт:** DPI = IP + ASN + порт + поведение; Reality `:443` база; xhttp (`jam-41`) — **после** P9 если TCP душат; SNI должен совпадать с ASN.

### 19.4 Как тестировать HTTPS / наш ресурс сейчас

| Что | Как | Доказывает | Не доказывает |
|-----|-----|------------|---------------|
| Сайт Аладдин | `curl -sS -o /dev/null -w '%{http_code}\n' https://aladdin-ai.ru/` | nginx `:443` | VPN LTE |
| Витрина | `curl … https://aimonkeystars.ru/` | NEW nginx | VPN |
| Порты NEW | `nc -z 37.46.134.98 8444` (8445, 5443) | TCP с **вашей** сети | LTE |
| `/sub/` | Brain или aim с `User-Agent: Happ` + `X-HWID` | JSON bundle | LTE до двери |
| **VPN LTE** | Телефон Happ · staging TID · **ночь LTE** | Data-plane | — |

**Важно:** `curl https://aladdin-ai.ru` = **сайт**, не VPN. PASS P9 = новая дверь **другого ASN :443** OK на LTE при том что NEW может FAIL.

### 19.5 Следующий шаг (канон)

1. **Не** GO all jam-40 · **не** MAIN443 на FirstVDS снова.  
2. **P9:** `jam-20` GO бюджета → `jam-21…24` → LTE ночь → GO профиля.  
3. CDN `jam-50/51` — отдельно.  
4. UX `fro-01/02`, `jam-13` — после P9 PASS.

**Registry:** `.cursor/VPN_JAMMING_TASK_REGISTRY.md` · **Next = P9**.

### 19.6 SNI policy — не использовать `vk.com` (2026-08-28, подтверждено на LTE)

| Факт | Детали |
|------|--------|
| **Симптом** | Staging TID `493897224` · jam-40 · 🇫🇮 FI с SNI **`vk.com`**: Wi‑Fi ✅ · **LTE ❌** (timeout) |
| **Контроль** | 🇩🇪 `max.ru`, 🇳🇱 `yandex.ru`, 🇵🇱 `cloudflare`, 🇸🇪 `yandex.ru` на **том же** NEW `:8444` — **LTE ✅** |
| **Вывод** | **`vk.com` / `www.vk.com` не выдаём клиентам** — DPI LTE режет SNI VK на non-VK IP/ASN |
| **Fix prod** | Brain `VPN_EU_REALITY_SNI_FI=max.ru` · bak `env.bak-fi-sni-*` · FI снова LTE ✅ |
| **NEW server** | **2026-08-28 GO:** `:8444` `serverNames` **без** `vk.com` · bak `config.json.bak-rm-vkcom-*` |
| **Dendi** | У конкурента `vk.com` на **своём** ASN (Citytelecom и др.) — **не** копируем на FirstVDS/NEW |

**Разрешённые SNI для AiMonkey EU (канон):** `max.ru` (основа) · `yandex.ru` / `www.yandex.ru` · при необходимости `www.cloudflare.com`.  
**Запрещено в `/sub/`:** `vk.com`, `www.vk.com` — не jam-40, не P9, не staging.

Код: `settings.py` default FI = `max.ru` · `apply_jam40_eu_sni_pool_staging.sh` · `subscription_util.py` policy note.

### 19.7 jam-41 — xhttp/gRPC lab **без покупки VPS** (LTE)

**Runbook:** `deploy/runbooks/JAM41_XHTTP_GRPC_LTE_LAB_WITHOUT_NEW_VPS_2026-08-28.md`

| Вопрос | Ответ |
|--------|--------|
| Починит ли xhttp/gRPC на **MAIN — Аладдин (`…180`)** LTE без нового VPS? | **Нет** — MAIN443 TCP `:443` уже **FAIL LTE** (тот же **FirstVDS AS29182**). |
| Можно ли **протестировать** до P9? | **Да** — lab на **Brain `:8443` xhttp** (трек A, staging TID) и опц. **MAIN `:8444` xhttp** (трек B, GO) как **negative control**. |
| Ожидание LTE на FVDS/Contabo entry | **FAIL/timeout** → закрываем гипотезу «смена транспорта без смены ASN». |
| Когда xhttp/gRPC **имеет смысл для LTE** | **После** P9 PASS на **новом ASN** — если TCP Reality `:443` marginal (Dendi gRPC на REG.RU; Frosty xhttp×4). |

**Не повторять:** MAIN `:443` SNI-split (ни TCP, ни xhttp).

**Порядок:** (опц.) трек A → **jam-20…24** → (опц.) jam-41 post-P9 на новой двери.

### 19.8 jam-20 — сравнение провайдеров (P9 первая дверь)

**Критерии:** ASN ≠ **AS29182** · **:443** · дверь → WG → Brain · staging TID · LTE ночь · 2-й ASN через ~месяц.

| # | Провайдер | ASN | У Dendi/Frosty | Оценка 1-й двери |
|---|-----------|-----|----------------|------------------|
| 1 | **Yandex Cloud** | AS200350 | Dendi `84.201.165.181:443` | ⭐ **#1** |
| 2 | **Selectel** | AS49505 / AS50340 | класс RU DC | ⭐ **#2** (другая «улица») |
| 3 | **REG.RU** | AS197695 | Dendi `79.174.*`, gRPC | ✅ lab #2/#3 |
| 4 | **Citytelecom / Datahouse** | AS3175 | Dendi `62.152.*`, `185.229.9.*` | ✅ 2-я волна |
| 5 | **Timeweb** | AS9123 | не эталон | ⚠️ дешёвый тест only |
| 6 | **Cloud.ru / VK Cloud** | RU cloud | обзоры 2026 | 🔬 после YC |
| ⛔ | **FirstVDS** (NEW/MAIN) | AS29182 | наш entry | **нет** — LTE FAIL |
| ⛔ | **Contabo** как дверь | EU | Brain egress only | §14 FAIL |
| ⛔ | **Hetzner/DO/OVH** | EU mass | Dendi «страны» | не первая LTE-дверь |

**«100%» не существует** — стратегия **2–3 ASN + :443 + LTE drill**, как у Dendi (~31 entry).

**Whitelist-check:** до xray на новом IP — `https://` или nginx `:443` с **телефона LTE**; не открывается → другой IP/пул.

### 19.9 P9 — гибридный мост (NEW + новая дверь)

**SSOT:** `deploy/VPN_P9_HYBRID_BRIDGE_PLAN_2026-08-28.md`

| Часть | Сервер | Профили | Когда |
|-------|--------|---------|-------|
| **Старый мост** | NEW `…98` `:8444` / `:8445` / `:5443` | 🇪🇺×5 · 🌏×5 · `🇷🇺 LTE` | Wi‑Fi · день · **запас** |
| **Новый мост** | Yandex / Selectel / REG.RU `:443` | 1–3 новых в `/sub/` | **Ночь LTE** · основной обход |
| **Мозг** | Brain `…150` | `/sub/` · egress | **без смены** |

**Покупка обязательна** для ночного LTE (AS29182 FirstVDS режут целиком). **MAIN (`…180`)** — VPN снят, **не** P9.  
**Rollout:** `jam-20…24` → **`jam-24b`** hybrid GO в `/sub/` (добавить новую дверь, **не** удалять NEW).

### 19.10 jam-20 — провайдеры и ориентир цен (авг 2026)

Полная таблица: **`VPN_P9_HYBRID_BRIDGE_PLAN_2026-08-28.md` §4**.

| # | Провайдер | ASN | ~₽/мес (мост) | Роль |
|---|-----------|-----|---------------|------|
| 1 ⭐ | **Timeweb Cloud** | AS9123 | **900** | Habr 1027276 reroll IP | **#1 lab** |
| 2 ⭐ | **REG.RU** | AS197695 | **390** | Dendi · Free 6 мес | **#1 бюджет** |
| 3 | **Yandex Cloud** | AS200350 | **~1 900** | только если LTE PASS | после IP-check |
| 4 | **Citytelecom** | AS3175 | КП | Dendi LTE | 2-я волна |
| 5 | VK / MWS | RU | — | Habr / Frosty | эксперимент |
| 6 | **Selectel** | AS49505 | от **949** | TSPU 2026 | если IP PASS |
| ⛔ | FirstVDS / Contabo entry | — | — | наш FAIL | нет |

**Форумы SSOT:** `VPN_P9_FORUM_PROVIDER_RESEARCH_2026-08-28.md`

Цены — ориентир; перед оплатой калькулятор провайдера + **whitelist-check IP на LTE**.

### 19.11 P9 REG.RU — LIVE staging PASS (2026-08-29) + Ideal A ❌ (2026-09-01)

**Handoff (restore):** `deploy/ML_SYSTEM_HANDOFF_P9_REG_RU_LTE_NIGHT_2026-08-29.md` (**§5.1**)  
**Plan §8 / §8.2b:** `VPN_P9_HYBRID_BRIDGE_PLAN_2026-08-28.md`

| Элемент | Значение |
|---------|----------|
| Дверь | REG.RU `92.242.61.63` AS197695 |
| Вход | Reality TCP `:443` · xHTTP `:8443` `/xhttp-p9` |
| Hop (канон) | REG → **NEW `…98` `:8444`** → WG → Brain `…150` (**навсегда** на этой ВМ) |
| NIC / floating | `192.168.0.25` + floating NAT `…63` на роутере OpenStack |
| Ideal A (`…63` на NIC) | ❌ REG: **из-под NAT не вынести** · `jam-22b` cancelled |
| Staging | TID `493897224` · `VPN_SUBSCRIBE_P9_MODE=staging` (+ xhttp) |
| Owner | **PASS** оба ночных профиля |

**Не делать:** hop REG → публичный Brain `:8446`; прямой WG на floating; netplan с публичным `…63`; пример REG `/etc/network/interfaces` вслепую.  
**Next (P9):** REG можно оставить запасом. Прямая WG-дверь на **этой** REG ВМ невозможна.  
**Ночная канон-дверь с 2026-09-11:** **P01 Yandex** — **§19.12** (не REG).  
**`jam-24b`:** теперь про выдачу **Яндекс-ночи всем**, не про «включить REG всем как единственную ночь».

### 19.12 P01 Yandex ночная дверь — LIVE staging, LTE PASS (2026-09-12 ~04:47)

**SSOT (читать целиком, особенно §23):** `ML_SYSTEM_HANDOFF_P01_YANDEX_NIGHT_DOOR_2026-09-11.md`  
**Сравнение голый IP vs NLB + куда покупать:** `ML_SYSTEM_HANDOFF_P01_NLB_VS_BARE_IP_JAMMING_2026-09-12.md`

| Элемент | Значение |
|---------|----------|
| Вход телефона | NLB `84.201.151.20:443` TCP → `yandex1` Reality `:443` |
| Origin | `yandex1` `158.160.24.238` · `ru-central1-b` · внутри `10.129.0.30` |
| SSH origin | `yc-user@158.160.24.238` · ключ `aladdin_server` |
| Профиль | **🇷🇺 LTE — ночной вход** |
| Hop | **прямой WG** `10.10.0.6` → Brain `10.10.0.2:51821` → `:8446` · **без NEW** |
| Витрина | **LIVE всем** · `VPN_SUBSCRIBE_P01_MODE=all` (13.09) |
| Owner LTE | PASS 11.09 на голый `158.x` → FAIL 12.09 на том IP → **PASS 12.09 ~04:47 на NLB** |
| HTTP-CDN | **FAIL** (P01 §22) — не повторять |
| Всем | **нет** — GO `p01-yc-10` · шаги P01 **§23.4** |

**Не повторять с нуля:** ВМ+WG+Reality уже стоят. Рабочая схема = **NLB перед Reality**, не голый IP ВМ и не Cloud CDN.

**Если сожгут `84.201…`:** новый NLB (новый IP), та же ВМ — P01 **§23.5**. Карусель IPv4 ВМ — не первый шаг. Playbook **§14** = скорость видео, не эта дверь. `jam-50/51` = CDN для URL `/sub/`, убрано 29.08.

**Не делать:** `MODE=all` без GO; `wg-quick down` на Brain `wg-bridge`; hop-via-NEW на живом YC WG; Ideal A на REG; Contabo как вход.

**Что лучше сделать заранее (владелец выбрал 1, 2026-09-12):**

| # | Вариант | Статус |
|---|---------|--------|
| **1** | Золотой набор P01 в `~/ALADDIN_VPN_SAFE/P01_GOLDEN_DOOR_KIT/` (без секретов, без новой ВМ). Следующая ночь глушилок = часы, не с нуля. | **✅ сделано** |
| **2** | Купить тёплый Timeweb заранее — платите, пока Яндекс ещё жив. | не делали · отдельный GO |
| **3** | Ничего не готовить. | отвергнуто |

Новые сервера и `VPN_SUBSCRIBE_P01_MODE=all` без GO не трогаем. Клон: набор + P01 **§11.2**.

**Лестница для следующей ML (добавлено 2026-09-12 ~17:15, ничего выше не удаляли):**

Владелец зафиксировал порядок. Предлагать **так**, просто:

| # | Когда | Что предложить | Куда читать / жать |
|---|--------|----------------|---------------------|
| **Вариант 2 (сначала)** | Сожгли `84.201…`, соседний Яндекс ещё пускает | Новый **Network Load Balancer**, та же `yandex1`, сырой TCP `:443`. Flip `VPN_P01_PUBLIC_HOST`. Обновить подписку | P01 **§23.9** · клики `RUNBOOK_P01_YANDEX_NLB_PASSTHROUGH_CONSOLE_2026-09-12.md` блок «Вариант 2» |
| **Вариант 3** | **Новый** Яндекс-NLB тоже «нет сервера» на LTE | Timeweb Москва, IP на NIC, jam-21, Reality, WG `10.10.0.7`. Отдельный GO | P01 **§23.9** · набор `P01_GOLDEN_DOOR_KIT/` |
| **Всем** | **сделано 13.09** `p01-yc-10` | `MODE=all` · имя **🇷🇺 LTE — ночной вход**. Если вход мёртв — Вариант 2 | P01 **§23.4** |

Не предлагать вместо Варианта 2: CDN, ALB-HTTPS, REG, Mouth, Contabo-вход, карусель IPv4 ВМ.

**2026-09-12 ~21:21:** второй админ (TID `744254201`) — LTE «Яндекс ночь» **PASS**. Масштаб всем = peer-sync на `yandex1` (как NEW), не ручные ключи и не новый код. Ждать **GO синк**, потом `p01-yc-10`. P01 **§23.10**.

**2026-09-12 ~21:30–21:35 — GO синк сделан.** Автомат ключей на `yandex1` как на NEW. Витрина Happ/Incy всё ещё тест. Всем — только `p01-yc-10`.

**2026-09-12 ~22:41:** третий админ (TID `854726070`) добавлен в staging. Happ JSON: Яндекс NLB `:443` Reality есть; чужой TID без Яндекса. Ключ на двери уже был после синка. LTE на телефоне — обновить подписку. `MODE=all` нет.

**2026-09-13 ~23:57 — p01-yc-10 сделан.** Имя **🇷🇺 LTE — ночной вход**. `MODE=all`. Happ: paid+trial видят NLB `:443` Reality. Германия NEW `:8444`. Клиентам обновить подписку.

**2026-09-14 ~00:12:** P9 «для ночи» → **🇷🇺 LTE — резерв**. «Домашний Wi‑Fi» убран из `/sub/` (был только у владельца, `HYBRID_WIFI_STAGING=false`). Не рабочий вариант. Не включать hybrid снова.

**Если сожгут `84.201…` — не покупать сервер.** Новый NLB в том же кабинете Яндекса, та же `yandex1`, ключи уже там. Клиентам обновить подписку. Простыми словами: P01 **§23.11**. Клики — RUNBOOK блок «Вариант 2». Новый NLB тоже молчит на LTE → Timeweb, не ферма Яндексов.

