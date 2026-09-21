# Asmadey skills — план оставшихся задач

**Для владельца и другой ML-системы.**  
Инфраструктура интеграции (фазы 0–6) **закрыта** — см. [`ASMADY_SKILLS_ML_HANDOFF.md`](ASMADY_SKILLS_ML_HANDOFF.md).  
Этот файл = **что ещё сделать**: живые прогоны, ROI, GO-гейты, бизнес.

| Поле | Значение |
|------|----------|
| **Дата** | 2026-09-19 |
| **SSOT статусов** | [`ASMADY_SKILLS_TASK_REGISTRY.md`](ASMADY_SKILLS_TASK_REGISTRY.md) |
| **Правило** | Не внедрять `asm-50` / `asm-51` без явного GO |
| **TodoWrite** | Новые ids `asm-r-*` только `merge: true`; не затирать `orch-*` / `af-*` |
| **Как делать B·C·E** | [`ASMADY_WAVES_BCE_PLAN.md`](ASMADY_WAVES_BCE_PLAN.md) |

---

## Принципы

1. Сначала **реальные пилоты** на задачах ALADDIN (не новые skills «ради skills»).
2. Фаза 4 stubs — **по ROI** после пилотов или по явному запросу.
3. `asm-50` / `asm-51` — **стоп**, пока владелец не сказал GO.
4. Business — отдельные сессии; **не** в iOS release commit.
5. Коммит `.cursor/ASMADY*` / skills — **только** по просьбе владельца.

---

## Оглавление остатков

| Волна | ID | Суть | Блокер |
|-------|-----|------|--------|
| A | `asm-r-01` … `03` | Живые пилоты gates / humanizer / ajtbd | Живая задача |
| B | `asm-r-04` … `07` | ROI-прогон dual-review / ui-stress / anti-slop / hypothesis | Волна A или запрос |
| C | `asm-r-08` … `09` | adhd / mobile — on-demand | Запрос владельца |
| D | `asm-r-10` … `11` | diy-mcp / agent-reach | **GO + ToS** |
| E | `asm-r-12` | Business session | Запрос владельца |
| F | `asm-r-13` | git commit handoff-артефактов | Явная просьба commit |
| — | skip | Dark Factory, RN dump, Asmadey tree в orch | Никогда без пересмотра конституции |

---

## Волна A — обязательные живые пилоты

Skills уже в `.cursor/skills/`. Нужен **прогон на продукте**, запись результата в registry journal.

### `asm-r-01` — Пилот `aladdin-gates` (Voice или Antifake)

| | |
|--|--|
| **Зачем** | Проверить, что GATES реально снижают «закрыл без доказательств» |
| **Как** | Взять одну открытую задачу Voice Safety **или** Antifake Hub → в чате `@aladdin-gates` → записать 3–8 GATES → код/verify → закрыть только с PASS |
| **Доказательство** | Список GATES + что прошло (verify script / скрин / curl) в journal registry |
| **GO?** | Нет — можно стартовать без отдельного GO |
| **Статус** | ✅ 2026-09-19 — см. `ASMADY_PILOT_JOURNAL.md` (G6 device у владельца) |

### `asm-r-02` — Пилот `aladdin-humanizer-ru`

| | |
|--|--|
| **Зачем** | Убрать канцелярит в письме Apple или 1 экране OB |
| **Как** | Одно письмо App Review **или** копирайт одного OB → `@aladdin-humanizer-ru` (+ при воде `@aladdin-slop-monster`) |
| **Доказательство** | До/после 5–10 строк текста; владелец ок по тону |
| **GO?** | Нет |
| **Статус** | ✅ 2026-09-19 — SHORT §2 humanized; journal |

### `asm-r-03` — Пилот `aladdin-ajtbd`

| | |
|--|--|
| **Зачем** | Зафиксировать «работу родителя» до UI-правок |
| **Как** | Одна JTBD: проверить ссылку **или** голос ребёнка → `@aladdin-ajtbd` → краткий шаблон → решение по UX |
| **Доказательство** | ½ страницы JTBD + решение (что меняем / не меняем) |
| **GO?** | Нет |
| **Статус** | ✅ 2026-09-19 — JTBD «ссылка/голос» в journal; on-demand |

**Критерий волны A done:** ✅ journal `ASMADY_PILOT_JOURNAL.md` + вердикт агента: **on-demand** (не constantly). Владелец может переопределить.

---

## Волна B — ROI по stubs фазы 4

Запускать **после A** или если владелец назвал конкретный skill.

### `asm-r-04` — `aladdin-dual-review` на одном Swift PR/diff

| | |
|--|--|
| **Как** | После `swift-reviewer` / matt — один проход dual-review |
| **Метрика** | Нашёл ли ≥1 полезный дефект, который иначе упустили |
| **Решение** | constantly / on-demand / archive |
| **Статус** | ✅ 2026-09-21 — journal `asm-r-04`; **Keep on-demand**; **C-1/C-2 fixed (GO 2026-09-21)** |

### `asm-r-05` — `aladdin-ui-stress` на Antifake или Voice UI

| | |
|--|--|
| **Как** | Один экран: a11y, safe area, dark, длинный RU |
| **Метрика** | Список находок → в фикс или wontfix |
| **Статус** | ⬜ todo |

### `asm-r-06` — `aladdin-anti-slop-design` на маркетинговом/hero куске

| | |
|--|--|
| **Как** | Один surface (не ломая Figma OB без ТЗ) |
| **Метрика** | Убраны generic AI-паттерны без регресса бренда |
| **Статус** | ⬜ todo |

### `asm-r-07` — `aladdin-hypothesis` + AJTBD

| | |
|--|--|
| **Как** | Одна гипотеза Voice или Antifake: формулировка → метрика → эксперимент |
| **Метрика** | Гипотеза записана; решение go/no-go эксперимента |
| **Статус** | ⬜ todo |

---

## Волна C — later on-demand (не constantly)

### `asm-r-08` — Brainstorm `@aladdin-adhd-brainstorm`

| | |
|--|--|
| **Когда** | Сложная развилка продукта (не ежедневный код) |
| **Запрет** | Не вставлять в orch night runtime |
| **Статус** | ⬜ wait-request |

### `asm-r-09` — `@aladdin-mobile-ux-notes` без RN dump

| | |
|--|--|
| **Когда** | Нужны UX-референсы HIG; Figma/HIG остаются каноном |
| **Запрет** | Не Material / не React Native как стек |
| **Статус** | ⬜ wait-request |

*(sgr-core уже задокументирован в `ASMADY_SGR_CORE_VS_ORCH.md` — отдельной задачи на форк нет.)*

---

## Волна D — DEFERRED + GO (стоп по умолчанию)

### `asm-r-10` — diy-mcp-connector (`asm-50`)

| | |
|--|--|
| **Триггер GO** | Владелец: «нужен MCP с сайта X» |
| **Перед внедрением** | sandbox → skillspector PASS → ToS → SSRF/secrets → **не** в iOS/orch core |
| **Док** | [`ASMADY_DEFERRED_DIY_MCP.md`](ASMADY_DEFERRED_DIY_MCP.md) |
| **Статус** | ⏸ deferred |

### `asm-r-11` — agent-reach (`asm-51`)

| | |
|--|--|
| **Триггер GO** | Владелец: «нужен сбор с соцсети Y» (маркетинг/research) |
| **Перед внедрением** | ToS · PII · **вне** iOS commits · **не** в orch |
| **Док** | [`ASMADY_DEFERRED_AGENT_REACH.md`](ASMADY_DEFERRED_AGENT_REACH.md) |
| **Статус** | ⏸ deferred |

---

## Волна E — Business

### `asm-r-12` — Session pricing / growth / SEO / Metrika / landing

| | |
|--|--|
| **Когда** | Владелец открыл отдельную бизнес-сессию |
| **Запрет** | `git add` в `feat(build N)` / Wellness iOS |
| **Док** | [`ASMADY_BUSINESS_OUT_OF_IOS.md`](ASMADY_BUSINESS_OUT_OF_IOS.md) |
| **Статус** | ⬜ wait-request |

---

## Волна F — Репозиторий

### `asm-r-13` — Commit handoff + skills (по просьбе)

| | |
|--|--|
| **Что может войти** | `.cursor/ASMADY*.md`, `rules/external-skill-audit.mdc`, `rules/asmadey-skills-todo-ssot.mdc`, `skills/aladdin-*` (новые), `skills_sandbox/`, правки MASTER + orch-basics |
| **Что не входить** | `telegram_stars_shop_bot/`, `.env`, VPN secrets handoff |
| **Статус** | ⬜ wait-owner-commit-ask |

---

## Порядок исполнения (жёсткий)

```text
asm-r-01 → asm-r-02 → asm-r-03     # живые пилоты
    → (опционально) asm-r-04…07   # ROI stubs
    → asm-r-08…09 только по запросу
    → asm-r-10…11 ТОЛЬКО после GO
    → asm-r-12 по бизнес-запросу
    → asm-r-13 по просьбе commit
```

Параллелить можно: `asm-r-02` и `asm-r-03` после старта `asm-r-01`, если разные чаты/контексты.

---

## Acceptance «остатки закрыты» (для владельца)

Волна A done + journal в registry = **минимум done** для «пилоты прогнаны».  
Волны B–F = **не блокируют** продукт; закрываются по запросу / GO.

| Минимум | Расширенный |
|---------|-------------|
| R01–R03 ✅ + вердикт constantly/on-demand | + ROI R04–R07 |
| 50/51 остаются ⏸ без GO | R10/R11 только с GO |
| Business / commit — опционально | R12 / R13 |

---

## Журнал выполнения остатков

| Дата | ID | Результат |
|------|-----|-----------|
| 2026-09-19 | `asm-r-01`…`03` | Волна A: journal + SHORT §2; G1–G5 PASS; G6 device open |
| 2026-09-19 | commit | `71be91e7` handoff · `66d27a06` sandbox gitignore |
| 2026-09-21 | `asm-r-04` | Dual-review Voice/Antifake: C-1/C-2 Critical + High; Keep on-demand |
| 2026-09-21 | `asm-r-04` fix | GO: C-1 hasStrings/hasURLs · C-2 extractURL-only URL path · tests added |

---

## Связь с Cursor TODO

Рекомендуемые ids (создавать **только** когда владелец сказал «начинай остатки»):

- `asm-r-01` … `asm-r-13`  
- Не дублировать закрытые `asm-00` … `asm-60`  
- `merge: true` always  

**Конец плана остатков.**
