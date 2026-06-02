# Wellness — план и факт (кратко)

> Обновлено: 2026-06-01

## Есть ли «поддержка в чате» живыми людьми?

| | План | Факт в коде |
|--|------|-------------|
| Живой чат / оператор / психолог онлайн | **Нет** (§12 master plan: без живых коучей) | **Нет** — нет UI и API для оператора |
| Ответы пользователю | **Цифровой друг (ИИ)** в Companion | **Да** — `POST /api/ai/companion/chat` + wellness prefix / orchestrator |
| `psychological_support_agent` | Родитель включает **доступ ребёнка** к разделу wellness | **Не** отдельный человек; флаг consent в `wellness_router` |

**Вывод:** фраза «поддержка в чате» в документах означала **ответ ИИ-агента (Companion)**, не службу поддержки. В новых текстах пишем: **«цифровой друг (ИИ)»**.

## Поток (как в плане)

```
Hub / Check-in → (опросники) → один столп → чат Companion (ИИ) → journal / timeline
                     ↑
              код: wellness_orchestrator, pillar guard, ethics L3, trauma L2
```

## Jung на prod

| | План (после PO 2026-06-01) | Факт |
|--|----------------------------|------|
| `FEATURE_WELLNESS_JUNG` | Можно на prod | `deploy_wellness_p1.sh` выставляет **=1** |
| `FEATURE_WELLNESS_REFLECTIVE` | Можно на prod | **=1** |
| `FEATURE_WELLNESS_ORCHESTRATOR` | Полный loop | **=1** |
| Откат для Apple | — | `.env` на VPS: `JUNG=0`, `REFLECTIVE=0` |

Политика и App Review: [legal/WELLNESS_PRIVACY_ADDENDUM.md](./legal/WELLNESS_PRIVACY_ADDENDUM.md).

## Два «orchestrator» — не путать

| Флаг / модуль | Назначение |
|---------------|------------|
| `FEATURE_WELLNESS_ORCHESTRATOR` + `wellness_orchestrator.py` | Wellness Loop: triggers → pillar → pack → agent hints → chat prefix |
| `COMPANION_USE_ORCHESTRATOR` + `orchestrator.py` | Stub multi-agent Hermes (общий Companion), **не wellness** |

Агенты wellness (`cbt_coach_agent`, …) — **роли в одном LLM-вызове** (`[WELLNESS AGENTS ACTIVE]` + `tools_used`), не отдельные модели.

## p3-20 pack_version

Сессия фиксирует `session_pack_folder` + `session_pack_version` при выборе столпа; prefix содержит `pack_version=cognitive_v1.0` и т.д.

## p3-05 GDPR

`GET /api/wellness/export/personal` · `DELETE /api/wellness/data` (сброс wellness consent).

## p0-08

| | Факт |
|--|------|
| Чеклист | [WELLNESS_CLINICAL_REVIEW.md](./WELLNESS_CLINICAL_REVIEW.md) — PO self-review ☑ |
| Внешний психолог/юрист | Не привлекался (решение PO) |
