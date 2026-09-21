# ML SYSTEM — START HERE (единая точка входа)

**Для владельца и любой другой ML / AI-системы.**  
Открой **этот файл первым**. Дальше — только по таблице маршрутов. Не читай весь репозиторий «на удачу».

| Поле | Значение |
|------|----------|
| **Роль файла** | Роутер + дорожная карта + конституция (не энциклопедия домена) |
| **Дата снимка** | 2026-09-21 |
| **Рабочий корень** | `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS` |
| **Перед правками** | `git rev-parse --show-toplevel` · `git branch --show-current` · `git status --short` |
| **Общие правила репо** | [`AGENTS.md`](../AGENTS.md) |
| **Как владелец передаёт задачу** | См. §8 ниже (одна фраза + этот файл) |

---

## 0. За 60 секунд

В репо живут **три продукта** (не смешивать коммиты/контекст без нужды):

| Продукт | Где | Прод |
|---------|-----|------|
| **iOS app ALADDIN** | корень репо (Swift) | App Store / TestFlight |
| **Coding Orchestrator** | `coding_orchestrator/` | Mac app + night agents |
| **Telegram bot / VPN API** | `telegram_stars_shop_bot/` · `aladdin_shop_vpn_api/` | Contabo / FirstVDS — **не** в iOS-релизные коммиты |

**Сейчас (снимок 2026-09-21):**

| Трек | Статус | Следующий шаг |
|------|--------|----------------|
| Coding Orchestrator | **115/115 ✅** | Пользоваться MASTER; новые фичи orch — только по задаче владельца |
| Asmadey → Cursor skills | Инфра ✅ · волна A ✅ · **B1 dual-review ✅** · **C-1/C-2 fixed** | B2 ui-stress / B3–B4 по фразе; C/E по запросу; D только с GO |
| Voice Safety Log (Variant C) | Код P0–P2 ✅ | **DEVICE QA** владельца (G6) · опционально GO на фикс C-1/C-2 из dual-review |
| Внешние skills | Шлюз ✅ | Всегда: sandbox → skillspector → **GO владельца** |

**Не делать «закрыть все волны Asmadey пачкой».** Лучший порядок: этот START_HERE → DEVICE Voice → волна B по одной задаче.

---

## 1. Конституция (нарушать нельзя без явного GO владельца)

1. **Корень** — только путь iOS выше; не править из parent-директорий.  
2. **Секреты** — никогда не коммитить/не вставлять в чат `.env`, токены, VPN handoff §32 (`VPN_SPEED_DEGRADATION_HANDOFF_RU.md`).  
3. **bot ≠ iOS release** — не `git add telegram_stars_shop_bot/` в iOS-релизные коммиты.  
4. **no-mock bypass** — parental / family / antifake: без `sfm_mock` / mock_fallback в проде.  
5. **ask-before-ops** — деплой, SSH/prod, restart, `.env`, xray: сначала спросить владельца.  
6. **Asmadey** — не vendor весь каталог в git; не Dark Factory auto-merge; не RN/shadcn/MagicUI как стек app.  
7. **TodoWrite** — только `merge: true` на треки `orch-*` / `asm-*` / `vsl-c-*` / `af-*`; не затирать чужие списки.  
8. **Коммит** — только если владелец явно попросил.

Приоритет при конфликте: **доменный MASTER/handoff + registry** > чужие skills > общая болтовня модели.

---

## 2. Дорожная карта (что делать дальше)

```text
[СЕЙЧАС]
  1. Владелец: Voice Safety DEVICE QA
       → docs/VOICE_SAFETY_LOG_P0_MANUAL_QA_RU.md
       → docs/VOICE_SAFETY_LOG_P2_MANUAL_QA_RU.md  (G6: виджет + неделя)
  2. По фразе владельца: Asmadey волна B — ОДИН skill за раз
       → .cursor/ASMADY_WAVES_BCE_PLAN.md
       → journal в .cursor/ASMADY_PILOT_JOURNAL.md

[ПО ЗАПРОСУ]
  · Волна C — brainstorm / mobile UX notes
  · Волна E — pricing / growth / SEO (вне iOS commits)
  · Companion / Antifake / VPN / Bot — свои handoff (таблица §3)

[ТОЛЬКО ЯВНЫЙ GO]
  · Волна D — diy-mcp (asm-50) / agent-reach (asm-51)
  · Prod deploy / SSH / merge в protected без Approve

[НЕ НУЖНО «ДОДЕЛАТЬ ВСЁ СРАЗУ»]
  · Не закрывать B+C+D+E пачкой
  · Не ставить 85 skills Asmadey
```

### Acceptance «минимум done» для текущего горизонта

| # | Критерий | Кто |
|---|----------|-----|
| M1 | P0 Voice manual QA отмечен владельцем | Владелец |
| M2 | P2 Voice (виджет + неделя) G6 отмечен | Владелец |
| M3 | Волна B: ≥1 ROI-пилот с вердиктом keep/archive в journal | ML по фразе |
| M4 | START_HERE актуален (дата + next step) | ML при смене горизонта |

---

## 3. Маршрутизатор (задача → один канон)

| Если задача про… | Сначала открой | Затем (по ссылкам внутри) |
|------------------|----------------|---------------------------|
| **Coding Orchestrator** (Mac, ночь, Telegram orch, Approve) | [`coding_orchestrator/docs/CODING_ORCHESTRATOR_MASTER.md`](../coding_orchestrator/docs/CODING_ORCHESTRATOR_MASTER.md) | `.cursor/CODING_ORCHESTRATOR_TASK_REGISTRY.md` |
| **Asmadey / Cursor skills / волны A–F** | [`.cursor/ASMADY_SKILLS_ML_HANDOFF.md`](../.cursor/ASMADY_SKILLS_ML_HANDOFF.md) | `ASMADY_SKILLS_REMAINING_PLAN.md` · `ASMADY_WAVES_BCE_PLAN.md` · `ASMADY_PILOT_JOURNAL.md` · registry `asm-*` |
| **Новый чужой skill** | [`.cursor/rules/external-skill-audit.mdc`](../.cursor/rules/external-skill-audit.mdc) | `@aladdin-skillspector` · `.cursor/skills_sandbox/` · ждать GO |
| **Voice Safety Log** | [`docs/ML_SYSTEM_HANDOFF_VOICE_SAFETY_LOG_VARIANT_C_2026-09-18.md`](ML_SYSTEM_HANDOFF_VOICE_SAFETY_LOG_VARIANT_C_2026-09-18.md) | REVIEW_RECS companion · `VOICE_SAFETY_LOG_*_MANUAL_QA_RU.md` · код `Core/Voice/` · `ClipboardSafetyService` |
| **Общие правила iOS / карта skills** | [`AGENTS.md`](../AGENTS.md) | `.cursor/skills/aladdin-*` · rules |
| **Antifake** | [`.cursor/ANTIFAKE_ML_HANDOFF_FOR_NEXT_AGENT.md`](../.cursor/ANTIFAKE_ML_HANDOFF_FOR_NEXT_AGENT.md) | `.cursor/ANTIFAKE_V4_TASK_REGISTRY.md` |
| **Companion / Rive** | [`docs/COMPANION_ML_HANDOFF_START_HERE.md`](COMPANION_ML_HANDOFF_START_HERE.md) | `COMPANION_ML_RIVE_HANDOFF_MASTER.md` |
| **App Review 2.1** | [`docs/AppStore/ML_SYSTEM_HANDOFF_GUIDELINE_2_1_2026-09-09_RU.md`](AppStore/ML_SYSTEM_HANDOFF_GUIDELINE_2_1_2026-09-09_RU.md) | SHORT reply · `@aladdin-humanizer-ru` |
| **Telegram bot** | `telegram_stars_shop_bot/docs/ML_SYSTEM_HANDOFF_FINAL.md` + deploy-safe rule | **Не** в iOS commit |
| **VPN / глушилки** | `aladdin_shop_vpn_api/deploy/VPN_RU_ENTRY_CLONE_AND_SCALE_PLAYBOOK_RU.md` §0.3 | naming rule · **не** push secrets handoff |
| **Backend iOS API** | `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md` | ask-before-ops |

Если тема **неясна** — спроси владельца одной фразой: «Это orch / skills / Voice / antifake / bot / VPN?»  
Не угадывай прод-действия.

---

## 4. Asmadey — сжатый статус (детали в handoff)

| Блок | Статус | Что делать ML |
|------|--------|----------------|
| Аудит (sandbox → skillspector → GO) | ✅ | Соблюдать всегда |
| Skills «брать» (`aladdin-gates`, humanizer, ajtbd, …) | ✅ | Вызывать `@aladdin-*` **по нужде** |
| Волна A (R01–R03) | ✅ journal | on-demand; не constantly |
| Волна B (R04–R07) | ⬜ | Только по фразе владельца; один skill; journal + ROI |
| Волна C | ⏸ | По запросу (brainstorm / UX notes) |
| Волна D (asm-50/51) | 🛑 | Без явного GO + ToS — **стоп** |
| Волна E бизнес | ⏸ | Отдельная сессия; вне iOS commits |

Канон: [`.cursor/ASMADY_SKILLS_ML_HANDOFF.md`](../.cursor/ASMADY_SKILLS_ML_HANDOFF.md).

Полезные вызовы в чате (когда уместно):  
`@aladdin-gates` · `@aladdin-humanizer-ru` · `@aladdin-ajtbd` · `@aladdin-skillspector` · `@aladdin-dual-review` · `@aladdin-ui-stress`.

---

## 5. Voice Safety Log — сжатый статус

| Слой | Статус |
|------|--------|
| План Variant C + review gaps | ✅ docs |
| Код P0 (router, ClipboardSafety, sheet→Antifake, coach) | ✅ |
| Код P1/P2 (now/shortcut, weekly, idea/remind, widget; EventKit OUT) | ✅ в коде |
| Ручной QA на устройстве | ⬜ владелец (P0 + P2 / G6) |

Канон: [`docs/ML_SYSTEM_HANDOFF_VOICE_SAFETY_LOG_VARIANT_C_2026-09-18.md`](ML_SYSTEM_HANDOFF_VOICE_SAFETY_LOG_VARIANT_C_2026-09-18.md).

---

## 6. Coding Orchestrator — сжатый статус

| Поле | Значение |
|------|----------|
| Статус | **115 / 115 ✅** |
| Канон | [`coding_orchestrator/docs/CODING_ORCHESTRATOR_MASTER.md`](../coding_orchestrator/docs/CODING_ORCHESTRATOR_MASTER.md) |
| App | `~/Applications/Coding Orchestrator.app` (Launchpad) |
| Asmadey | **Не** каталог внутри orch — только GATES note + ссылка на `.cursor/ASMADY*` |

Другой ML по orch: достаточно MASTER. Не дублировать Asmadey внутрь orch.

---

## 7. Алгоритм работы следующей ML-системы

1. Прочитай **этот** START_HERE (§0–§2, §1 конституция).  
2. Уточни задачу владельца (одна фраза). Если нет — спроси.  
3. Открой **один** канон из §3.  
4. Следуй handoff: TDD / GATES / ask-before-ops / merge-only TODO.  
5. Не расширяй scope (не «заодно» bot+VPN+iOS).  
6. В конце: что сделано · какие файлы · что осталось · нужен ли GO/DEVICE.  
7. При смене горизонта next-step — обнови дату/таблицу §0 в **этом** файле (или попроси владельца).

### Smoke (быстрая проверка, что входы на месте)

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
test -f docs/ML_SYSTEM_START_HERE.md \
 && test -f coding_orchestrator/docs/CODING_ORCHESTRATOR_MASTER.md \
 && test -f .cursor/ASMADY_SKILLS_ML_HANDOFF.md \
 && test -f docs/ML_SYSTEM_HANDOFF_VOICE_SAFETY_LOG_VARIANT_C_2026-09-18.md \
 && test -f AGENTS.md \
 && echo "START_HERE smoke OK"
```

---

## 8. Как владелец передаёт задачу (копипаст)

**Шаблон A — универсальный**

```text
Прочитай docs/ML_SYSTEM_START_HERE.md и действуй только по нему.
Задача: <одна фраза>.
Не трогай другие домены. Коммит только если я попросил.
```

**Шаблон B — Asmadey волна B**

```text
Прочитай docs/ML_SYSTEM_START_HERE.md → .cursor/ASMADY_WAVES_BCE_PLAN.md.
Сделай только asm-r-04 dual-review на Voice Safety / Antifake diff.
Запиши вердикт в ASMADY_PILOT_JOURNAL.md. Без коммита.
```

**Шаблон C — только Orch**

```text
Единый вход: coding_orchestrator/docs/CODING_ORCHESTRATOR_MASTER.md
(START_HERE §6). Задача: <…>.
```

**Шаблон D — Voice DEVICE (для человека; ML готовит чеклист)**

```text
По START_HERE §5 / §2: подготовь краткий чеклист из
VOICE_SAFETY_LOG_P0 и P2 MANUAL_QA — что нажать на iPhone. Код не менять.
```

---

## 9. Canvas (опционально, в Cursor)

| Canvas | Зачем |
|--------|-------|
| `aladdin-what-next-board` | Статус-доска: сделано / осталось |
| `asmadey-skills-aladdin-analysis` | Каталог ~85 skills + вердикты |

Не заменяют этот файл и доменные MASTER.

---

## 10. Карта ключевых файлов (шпаргалка)

| Файл | Роль |
|------|------|
| `docs/ML_SYSTEM_START_HERE.md` | **Этот файл — вход №1** |
| `AGENTS.md` | Конституция репо + карта skills/rules |
| `coding_orchestrator/docs/CODING_ORCHESTRATOR_MASTER.md` | Orch SSOT |
| `.cursor/ASMADY_SKILLS_ML_HANDOFF.md` | Asmadey SSOT для ML |
| `.cursor/ASMADY_SKILLS_REMAINING_PLAN.md` | Остатки asm-r-* |
| `.cursor/ASMADY_WAVES_BCE_PLAN.md` | Как делать волну B/C/E |
| `.cursor/ASMADY_PILOT_JOURNAL.md` | Журнал пилотов |
| `.cursor/ASMADY_SKILLS_TASK_REGISTRY.md` | Статусы asm-* |
| `docs/ML_SYSTEM_HANDOFF_VOICE_SAFETY_LOG_VARIANT_C_2026-09-18.md` | Voice план+код |
| `docs/VOICE_SAFETY_LOG_P0_MANUAL_QA_RU.md` | Voice QA P0 |
| `docs/VOICE_SAFETY_LOG_P2_MANUAL_QA_RU.md` | Voice QA P2 / G6 |

---

## 11. One-paragraph (для статуса)

**Единый вход для любой ML — `docs/ML_SYSTEM_START_HERE.md`.** Дальше по маршруту: Orch MASTER · Asmadey handoff · Voice handoff · AGENTS. Оркестратор 115/115 готов; Asmadey-инфра и волна A готовы; волна B — по одной фразе; C/E по запросу; D только с GO. Voice Safety в коде — ждёт DEVICE QA владельца. Не dump Asmadey, не auto-merge, не смешивать bot/VPN в iOS-релиз без задачи.

---

*Конец START_HERE. Следующий агент: §7.*
