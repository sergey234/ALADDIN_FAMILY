# Companion — задачи БЕЗ Rive (параллельная очередь)

> **Стратегия:** Rive Editor / production `.riv` — **блокер**, делаем **в конце** после подключения.  
> **Этот список** — всё, что можно закрыть **сейчас** на placeholder `.riv` + PNG bridge.  
> **Handoff:** [COMPANION_ML_HANDOFF_2026-05-29.md](./COMPANION_ML_HANDOFF_2026-05-29.md) · **Трекер:** [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md)  
> **План кода v2:** [COMPANION_CODE_PLAN_NO_RIVE.md](./COMPANION_CODE_PLAN_NO_RIVE.md) · **Трекер v2:** [COMPANION_CODE_TODO_TRACKER.md](./COMPANION_CODE_TODO_TRACKER.md)  
> **PO 29.05:** 🦄🧑🧞 — **три героя доступны всем**; PG + consent без ослабления.  
> **Обновлено:** 2026-05-29 · **CODE Sprints 0–3 ✅** · **102-tracker: 76/102**

**Правило:** задачи с пометкой **🟡 финал после Rive** — начинать можно, закрывать `[x]` только после визуальной части или явного PO «OK на placeholder».

---

## Приоритет 0 — сегодня (iOS, без Rive)

| ID | Задача | Действие | Статус |
|----|--------|----------|--------|
| **iOS-POL-11** | STT на реальном iPhone | ✅ код build **214** · device QA ⏳ |
| **iOS-POL-12** | Карточка «Мир героев» на Child Rewards | ✅ |
| **P1-13g** | = iOS-POL-11 | ✅ код |
| **GATE-P0** (часть) | **SPEECH-Q6** в 11b | ⏳ после TF **214** |

---

## Приоритет 1 — iOS UX / навигация (без Rive)

| ID | Задача | Статус |
|----|--------|--------|
| **UX-06** | Big button «Друзья» → Companion | ✅ |
| **UX-07** | Ссылка из unicornPet | ✅ |
| **UX-08** | Legacy navigation → `companionHome` | ✅ |
| **UX-09** | GATE навигации R6/R8 | ⏳ QA |
| **UX DoD** | Один push Kids → Companion Home | ✅ (код) |

---

## Приоритет 2 — голос / бэкенд (без Rive)

| ID | Задача | Статус |
|----|--------|--------|
| **P1-13d** | WS голос без stub | ✅ |
| **P1-13** | Голос production E2E | ✅ |
| **P0-04 доработка** | Voice realtime не stub | ✅ |

---

## Приоритет 3 — P1+ Production (все без Rive)

| ID | Задача | Статус |
|----|--------|--------|
| **P1-12** | Postgres + Redis | ⏳ Sprint 4 |
| **P1-14** | XCUITest | ✅ |
| **P1-15** | prod verify | ✅ |
| **P1-16** | ADR hot path | ✅ |
| **P1-17** | Accessibility | ✅ |
| **P1-18** | Rate limit 429 | ✅ |
| **P1-20** | RU/EN l10n | ✅ |
| **P1-21** | Offline cache | ✅ |
| **P1-22** | Post-LLM moderation | ✅ |
| **P1-19** | App Store pack doc | ✅ · **3 Hub screenshots ⏳** |

**P1-23 / GATE-EMO:** логика эмоций в BE+iOS **уже есть**; полный DoD **ждёт Rive** — не ставить `[x]` на GATE-EMO до 07.

---

## Приоритет 4 — GATE / QA диалоги (большей частью без Rive)

| ID | Задача | Без Rive? |
|----|--------|-----------|
| **GATE-OPS** | health + verify prod | ✅ |
| **GATE-CX** | 5 фраз CX | ✅ |
| **GATE-P1** | cosmetics, legal | ✅ |
| **GATE-DIALOG-REGRESS** | R1–R19 (14/19 auto ✅) | ✅ добить оставшиеся |
| **GATE-DIALOG** | D01–D10 текстовые сценарии TestFlight | ✅ (лица D10 🟡 после Rive) |
| **GATE-EMO-EMPATHY** | 5 мин диалог child/teen/senior | ✅ контент/тон; визуал героя 🟡 |
| **GATE-P2/P3** | после PROD | ✅ позже |

---

## Приоритет 5 — P2 фаза B (без Rive, кроме P2-09)

| ID | Задача |
|----|--------|
| **P2-01** | web search |
| **P2-02** | orchestrator |
| **P2-03** | Fast/Reasoning/Think |
| **P2-04** | фото и PDF |
| **P2-05** | trust decay/streak |
| **P2-06** | family context в промпте |
| **P2-07** | Responses API |
| **P2-08** | COGS dashboard |
| **P2-12** | life domains API |
| **P2-13** | social bridge |
| **P2-14** | вход Senior 60+ (навигация/копирайт — без Rive; визуал 🟡) |
| **P2-15** | teen loneliness playbook |
| **P2-16** | trust за эмпатию |

**НЕ без Rive:** **P2-09** (Figma↔Rive), **P2-17** (после HERO-3).

---

## Приоритет 6 — P3 и Adult (без Rive)

| ID | Задача |
|----|--------|
| **P3-01…04** | картинки, видео, workspaces, контекст (BE) |
| **P3-05** | Android (отдельный проект) |
| **P3-06** | Adult iOS Store |
| **A-01…03** | Adult OpenAPI, policy tests, repo stub |

---

## Приоритет 7 — продукт / дизайн (без Rive runtime)

| Задача | Примечание |
|--------|------------|
| Emoji audit → SF Symbols (Main, Settings) | Не требует `.riv` |
| AI Hub teaser на Main (отдельный от Assistant) | Продукт + макет |
| Документация / runbooks | Всегда ✅ |

---

## Что НЕ входит в этот список (только Rive)

| ID | Почему |
|----|--------|
| **HERO-3-07** | Export production `.riv` |
| **HERO-3-11b** MOTION-Q, MIMIC-Q, **D10** | Качество движения/лица в Rive |
| **HERO-3-11c** | После 07 |
| **GATE-EMO** | 13 state + Rive визуал |
| **P1-08 финал** | = 07 |
| **P2-09** | Figma↔Rive |
| **P2-17** | После HERO-3 |

---

## Рекомендуемый порядок (обновлено 2026-05-29)

```text
Сделано (Sprints 0–3): UX+3 героя, voice/l10n/offline, XCUITest, 429, moderation, ADR, Store doc

Следующий код (Sprint 4):
  P1-12 Postgres/Redis → P2-02 orchestrator → P2-12/13/15/16

После TF 214:
  11b SPEECH-Q6 device → GATE-DIALOG D01–D05 → UX-09

После Rive:
  07 → 11b MOTION/MIMIC/D10 → 11c → GATE-EMO → P1-19 screenshots
```

---

*Обновлять вместе с [TRACKER](./COMPANION_PROGRESS_TRACKER.md).*
