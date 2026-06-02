# Инструкция для другой ML-системы (Cursor / Claude / GPT)

> **Назначение:** передать проект Wellness Platform так, чтобы новый агент на **100%** понял *что*, *зачем* и *как* делать — и синхронизировал **131 TODO** с панелью Cursor.  
> **Канонический план:** [WELLNESS_PLATFORM_MASTER_PLAN.md](./WELLNESS_PLATFORM_MASTER_PLAN.md) **v2.5** (§4.3 Knowledge Pack)  
> **Чеклист задач:** [WELLNESS_CURSOR_TODO.md](./WELLNESS_CURSOR_TODO.md) — **131 задача**

---

## 0. Первое сообщение (скопируйте агенту целиком)

```text
Ты — senior full-stack (iOS SwiftUI + Python FastAPI) для ALADDIN Wellness Platform.

Рабочая папка ТОЛЬКО:
/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

Прочитай в порядке:
1) docs/WELLNESS_ML_HANDOFF.md (этот файл)
2) docs/WELLNESS_IMPLEMENTATION_STATUS.md (что уже сделано + деплой)
3) docs/WELLNESS_PLATFORM_MASTER_PLAN.md
4) docs/WELLNESS_CURSOR_TODO.md

Сделай Шаг A (подтверждение) из §3 — таблица «понял / риски / порядок».
Затем Шаг B: импорт 131 задачи в Cursor TODO (§3, §10).
Фазы 0–3 + §18 ЗАКРЫТЫ (131/131) — не переделывать без PO. Дальше: App Store, canary, Postgres cutover.
Перед deploy — §0.1 и WELLNESS_IMPLEMENTATION_STATUS.md «Деплой backend».

Жёсткие запреты:
- Не «AI психотерапевт» в UI; только «цифровой друг», «эмоциональная поддержка», «Глубокое исследование»
- Один столп = одна сессия LLM (не смешивать CBT+Jung+habit в одном ответе)
- Child 8–12: только 2 кнопки Hub; без PHQ-9, без дневника снов
- Parent НЕ видит дословный чат teen
- Без PPG/камеры стресса; без живых коучей
- Production parental bypass: без mock (см. .cursor/rules/prod-no-mock-bypass.mdc)
- Кризис L3: companion_ethics.py — 112, блок deep mode

Позиционирование: «Семейный цифровой друг» + мост к живым людям, не замена психолога.
```

---

## 0.1 Прод-сервер (перед deploy wellness API)

**Файл:** [ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md](../ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md)

| Шаг | Команда / действие |
|-----|-------------------|
| Health | `curl -s -S -m 8 http://149.154.65.180:8002/api/health` |
| SSH | `ssh -o IdentitiesOnly=yes -i ~/.ssh/aladdin_prod root@149.154.65.180` |
| Backend | `/opt/aladdin-backend` — `app/routers/`, `py_compile`, restart gunicorn/systemd |
| Wellness код | `security/services/ai_platform/wellness_*.py` → scp по runbook гайда |

Пароли **не** в репозитории. Правило: `.cursor/rules/aladdin-server-connection.mdc`.

---

## 1. Карта документов (что читать и зачем)

| # | Файл | Роль |
|---|------|------|
| 1 | **WELLNESS_PLATFORM_MASTER_PLAN.md** | Архитектура, 4 столпа, **§4.3 Knowledge Pack**, фазы, API |
| 2 | **WELLNESS_CURSOR_TODO.md** | **131 задача** с ID — единственный чеклист |
| 3 | **WELLNESS_IMPLEMENTATION_STATUS.md** | Статус 131/131, деплой VPS, plan vs fact |
| 4 | **WELLNESS_ML_HANDOFF.md** | Эта инструкция |
| 5 | **WELLNESS_I18N_CHECKLIST.md** | ~120 ключей `wellness_*` ru/en |
| 6 | **WELLNESS_I18N_GLOSSARY.md** | Запрещённые термины, тон child/teen |
| 7 | **WELLNESS_APPLE_HEALTHKIT_SETUP.md** | HealthKit: вариант A (Portal) / откат B — [WELLNESS_HEALTHKIT_ROLLBACK_PLAN.md](./WELLNESS_HEALTHKIT_ROLLBACK_PLAN.md) |
| 8 | `docs/ADR-WELLNESS-PLATFORM.md` | Фаза 0 ✅ |
| 9 | `docs/WELLNESS_ESCALATION_LADDER.md` | Фаза 0 ✅ |
| 10 | `docs/WELLNESS_CLINICAL_REVIEW.md` | Фаза 0 ✅ |
| 11 | `.cursor/rules/wellness-platform-expert.mdc` | Правило Cursor (авто-контекст) |
| 12 | `companion_ethics.py` | Кризис, этика |
| 13 | `ai_companion_router.py` | wellness_prefix |
| 14 | `wellness_knowledge/` | Knowledge Pack §4.3 |
| 15 | `wellness_prompt_builder.py` | `[WELLNESS v1]` |
| 16 | `LocalizationManager.swift` | i18n паттерн |

**Не сканировать весь репозиторий ALADDIN_NEW (~28GB)** — только путь iOS выше + `security/` на сервере в том же дереве.

---

## 2. Что мы реализуем (одним абзацем)

**Wellness Loop Engine** внутри существующего Companion: check-in → скрининг → **один из 4 столпов** (Разобрать мысли / Маленькие шаги / Принять себя / Понять себя) → чат/упражнения → journal/insights → outcome 24h → escalation L0–L3 → семейные алерты **без** текста чата teen. Family-first, не клон Jivi (без PPG, без мед. claims).

---

## 3. Обязательные шаги нового агента

### Шаг A — Подтверждение (до кода)

Агент отвечает **структурированно**:

1. **4 столпа** — названия UI + что внутри + age gating (таблица)
2. **Запреты** — список из §12 master plan (минимум 6 пунктов)
3. **Порядок фаз** — 0 → 1 → 2 → 3, что входит в gate каждой фазы
4. **Риски** — 3 главных (клиника, teen privacy, mix pillars)
5. **Первые 5 задач** — ID из WELLNESS_CURSOR_TODO.md

Если ответ расплывчатый — **не начинать код**.

### Шаг B — Загрузка ~120 TODO в панель Cursor

Cursor хранит TODO **в сессии агента** (инструмент TodoWrite). Markdown-файл **не** подхватывается автоматически.

**Вариант 1 (рекомендуется):** попросить агента:

```text
Импортируй все задачи из docs/WELLNESS_CURSOR_TODO.md в Cursor TODO:
- id = строка вида p0-01 (как в файле)
- content = русский текст задачи из файла
- status = pending, кроме p18-01 = completed
Используй TodoWrite merge:false для первого батча, merge:true для остальных.
Разбей на 4 батча по фазам (0, 1, 2, 3+i18n).
```

**Вариант 2 (ручной):** открыть `WELLNESS_CURSOR_TODO.md` → чекбоксы `- [ ]` — отмечать по мере работы; панель Cursor опциональна.

**Вариант 3:** новый чат + `@` файлы:
`WELLNESS_ML_HANDOFF.md`, `WELLNESS_IMPLEMENTATION_STATUS.md`, `WELLNESS_CURSOR_TODO.md`, `WELLNESS_PLATFORM_MASTER_PLAN.md`

**Вариант 4 (Cursor Rules):** скопировать чеклист в User Rule — неудобно для 131 пункта; предпочтительно TodoWrite.

### Шаг C — Правило Cursor

Убедиться, что активно правило:

`.cursor/rules/wellness-platform-expert.mdc`

(создано в v2.4 — подхватывается при работе с wellness-файлами и docs).

### Шаг D — Реализация

Следовать **ID задач** и **gate** из §4 ниже. После каждой закрытой задачи: обновить `[ ]` → `[x]` в `WELLNESS_CURSOR_TODO.md` + соответствующий Todo в Cursor.

---

## 4. Gate между фазами (когда можно идти дальше)

| Gate | Условие (все должны быть ☑) |
|------|-----------------------------|
| **0 → 1** | p0-01 ADR, p0-04/05 disclaimers, p0-07 copy, p0-11 escalation, p0-09 referral, p0-14/15 Knowledge Pack format, флаги p0-03 |
| **1 → 2** | Hub+check-in+consent iOS, wellness_router, PHQ-lite, pillar router v1, p1-26/27 prefix builder, p1-28 packs cognitive+humanistic, p1-22 guard, p1-29 smoke, p1-16, p1-14 i18n |
| **2 → 3** | ✅ **ЗАКРЫТ 2026-06-01** (51/51) — см. WELLNESS_IMPLEMENTATION_STATUS.md |
| **3 ship** | orchestrator, p3-12 premium gate, canary p3-10, PO checklist p0-08 |

---

## 5. Definition of Done (на каждую задачу)

- [ ] Код в правильном слое (iOS `Screens/` / `security/services/ai_platform/`)
- [ ] Feature flag если риск для prod
- [ ] ru+en ключи для **любого** user-visible текста (см. I18N checklist)
- [ ] Age gating проверен (child/teen/parent/senior)
- [ ] Нет смешения столпов в одном LLM-ответе (p1-22 / p2-15)
- [ ] Кризис не ослаблен vs `companion_ethics.py`
- [ ] Тест или smoke script для API-задач
- [ ] ID задачи в commit message: `wellness: p1-12 Hub screen`

---

## 6. Как делать «наилучшим образом» (принципы)

| Принцип | Действие |
|---------|----------|
| Минимальный diff | Одна задача = один PR/коммит где возможно |
| Переиспользовать | `companion_store`, `ai_companion_router`, `age_policy`, `LocalizationManager` |
| Не over-engineer | Фаза 1 без полного orchestrator — pillar router в router |
| Один столп | `wellness_pillar_guard.py` + system prompt per pillar |
| Этика | Любой Jung/сны — disclaimer; trauma → L2 referral, не EMDR |
| i18n | Сначала ключ в checklist, потом Swift/JSON |
| Сервер | Путь: `security/services/ai_platform/wellness_*.py` |

---

## 7. Синхронизация TODO ↔ Markdown

```
WELLNESS_CURSOR_TODO.md  ←→  Cursor Todo panel (TodoWrite)
         ↑
WELLNESS_PLATFORM_MASTER_PLAN.md §14, §19
```

При расхождении **побеждает** `WELLNESS_CURSOR_TODO.md` (рабочий список); master plan обновляет PO вручную.

---

## 8. Чеклист для PO (вы)

- [ ] Открыть новый Cursor Agent в `ALADDIN_iOS`
- [ ] Вставить сообщение из §0
- [ ] Дождаться Шага A (таблица подтверждения)
- [ ] Попросить Шаг B (импорт 120 TODO)
- [ ] Проверить, что правило `wellness-platform-expert.mdc` видно в Rules
- [ ] Сказать «Старт Фаза 3» (или §18) после OK на Шаг A

---

## 10. Как прикрепить 131 TODO в Cursor (как в этом чате)

Панель **TODO** в Cursor — это не файл в репо, а состояние агента через инструмент **TodoWrite**.

### Пошагово для PO

1. **New Agent** (Composer) в папке `ALADDIN_iOS`.
2. Вставить сообщение из **§0** (обновлённое).
3. Написать: *«Импортируй WELLNESS_CURSOR_TODO.md в TodoWrite: id=p0-01…, status=completed для всех [x], pending для [ ]. 4 батча.»*
4. Агент создаст ~131 пункт — в боковой панели Cursor появится список как в текущем чате.
5. При новом чате — повторить Шаг B или держать открытым `@WELLNESS_CURSOR_TODO.md` (чекбоксы в markdown не синхронизируются с панелью автоматически).

### Синхронизация двух источников

| Источник | Кто обновляет |
|----------|----------------|
| `docs/WELLNESS_CURSOR_TODO.md` | Агент после каждой задачи: `[ ]` → `[x]` |
| Cursor Todo panel | TodoWrite `merge:true` с тем же id `p2-36` |
| `WELLNESS_IMPLEMENTATION_STATUS.md` | Раз в спринт / при смене фазы |

**id обязан совпадать:** `p2-45`, не «Weekly meaning».

### Батчи для TodoWrite (подсказка агенту)

```
Батч 1: p0-01 … p0-16  (16) — все completed
Батч 2: p1-01 … p1-29  (29) — все completed
Батч 3: p2-01 … p2-51  (51) — все completed
Батч 4: p3-01 … p3-20 + p18-01 … p18-15 (35) — все completed
PO: po-clinical-signoff ✅ · po-verify-prod ✅ · po-healthkit ⏸ · po-healthkit-rollback-ci 📋

**CI build 221:** archive failed (HealthKit vs profile) — см. [WELLNESS_HEALTHKIT_ROLLBACK_PLAN.md](./WELLNESS_HEALTHKIT_ROLLBACK_PLAN.md). Код отката **не выполнять** без явной команды PO.

**PO (отложено):** HealthKit — вариант A [WELLNESS_APPLE_HEALTHKIT_SETUP.md](./WELLNESS_APPLE_HEALTHKIT_SETUP.md) · вариант B rollback [WELLNESS_HEALTHKIT_ROLLBACK_PLAN.md](./WELLNESS_HEALTHKIT_ROLLBACK_PLAN.md).
```

---

## 11. Статус (2026-06-01 — ЗАКРЫТО)

**131/131 задач ядра выполнены.** Ф0–Ф3 + §18 i18n = 100%.

**PO (не код):** HealthKit — см. rollback plan B (CI) или Portal A — docs выше.

**Deploy + verify после каждого выката:**

```bash
./scripts/deploy_wellness_p1.sh root 149.154.65.180 ~/.ssh/aladdin_server
./scripts/verify_wellness_prod.sh https://aladdin-ai.ru
```

Полная таблица: [WELLNESS_IMPLEMENTATION_STATUS.md](./WELLNESS_IMPLEMENTATION_STATUS.md) · [WELLNESS_CURSOR_TODO.md](./WELLNESS_CURSOR_TODO.md).

---

## 12. Частые ошибки других ML

| Ошибка | Правильно |
|--------|-----------|
| Смешать 4 школы в одном промпте | Один `primary_pillar` на сессию |
| «Терапия» в App Store | Self-help, emotional support |
| PHQ ребёнку 8 лет | Только teen+; child — emoji check-in |
| Mock bypass API в prod | Real API only |
| Grep всего ALADDIN_NEW | Только `mobile_apps/ALADDIN_iOS` |
| Пропустить Фазу 0 | ADR + legal + escalation обязательны |

---

**Ops handoff (только Postgres + Parent LLM):** [WELLNESS_POSTGRES_PARENT_LLM_HANDOFF.md](./WELLNESS_POSTGRES_PARENT_LLM_HANDOFF.md)

*Handoff v3.0 · 2026-06-01 · **131/131 (100%) CLOSED** · Ф0–Ф3 + §18 · + CANARY/POSTGRES runbooks*
