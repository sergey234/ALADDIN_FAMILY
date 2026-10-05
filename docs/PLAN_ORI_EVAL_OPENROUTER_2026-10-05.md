# Ori Eval × OpenRouter — план действий (2026-10-05)

**Цель:** выбирать модель под задачу по цифрам (quality / $/task / latency), не по лидербордам; не переплачивать; закрыть регрессии багов агента eval-ами.

**Для другой ML (главный план):** [`docs/ML_SYSTEM_HANDOFF_ORI_EVAL_2026-10-05.md`](ML_SYSTEM_HANDOFF_ORI_EVAL_2026-10-05.md)  
**SSOT задач:** [`.cursor/ORI_EVAL_TASK_REGISTRY.md`](../.cursor/ORI_EVAL_TASK_REGISTRY.md) · Cursor TODO ids `ori-*`  
**Канон инструмента:** [Ori Eval docs](https://openrouter.ai/docs/guides/ori/eval) · spawn: `curl -fsSL https://openrouter.ai/skills/spawn-ori-eval`

---

## 0. Контекст (что уже есть)

| Поверхность | Где | Модель сейчас | Боль |
|-------------|-----|---------------|------|
| Hermes / parent AI | MAIN `:8002` → OpenRouter | `deepseek/deepseek-v4-flash` | Огромный prompt; Pro → 402 на free-tier |
| Shop assistant | 🇩🇪 Brain Contabo | Flash → `deepseek-chat` → `:free` | При 402 free отвечает «ок» |
| ASA LLM | `security/services/asa/llm.py` | Hermes → chat → free chain | Тот же обвал качества |
| AI PM LLM-judge | `scripts/run_ai_pm_llm_judge.py` | `deepseek-chat` (opt live) | Судья должен быть дешёвым |

**Правило выбора:** самая дешёвая модель, которая проходит порог качества. Не max score.

---

## 1. GATES (закрытие фазы = все PASS)

| # | Gate | Доказательство |
|---|------|----------------|
| G1 | Нет family/child PII и live chat logs в fixtures Ori | Review `evals/**/fixtures` + policy в runbook |
| G2 | Бюджет первого live-прогона ≤ лимит пилота (default **$2**) | OpenRouter usage / report `$` |
| G3 | Кандидаты отфильтрованы `maxPromptPrice` (Flash-класс) | `candidateModels({…})` в `*.eval.ts` |
| G4 | Метрики: score + p50 latency + **$/completed task** | `ori eval --report` |
| G5 | Prod model **не** меняется без явного GO | Journal + diff env только после GO |
| G6 | Eval-файлы бота **не** в iOS release commit | `git diff --cached` без `telegram_stars_shop_bot` в iOS-релизе; bot evals в bot tree |
| G7 | CI: live Ori **не** в unit-job; только `workflow_dispatch` / monthly | `.github/workflows/ori-eval.yml` |
| G8 | Free-fallback «ок» не считается PASS | Deterministic asserts (tool call / mustMention) |

Hotfix без GATES запрещён для смены prod-модели.

---

## 2. Политика «не переплачивать»

1. **Порог → цена.** Pass = tool/fact asserts; не «красивый текст».
2. **Потолок в eval.** `maxPromptPrice` + `toCostAtMost` + `toFinishWithin`.
3. **$/completed task**, не $/token в вакууме (ретраи портят «дешёвую» модель).
4. **Дорогая модель только на узкий VIP-срез** (если классификатор среза дёшев; иначе одна модель).
5. **Judge дешевле испытуемого;** где можно — deterministic checks без LLM-judge.
6. **Не `openrouter/auto` для parental/family** (нужен контроль ZDR/провайдера).
7. **Не слать** реальные family logs / VPN secrets / §32 handoff в Ori.

Ориентир потолка входа (Flash-класс): порядка `$0.50 / 1M` prompt tokens → `maxPromptPrice: 0.0000005` (уточнять по live catalog на день прогона).

---

## 3. Фазы и порядок

```text
P0 Docs/GATES/Inventory
  → P1 Fixtures (synthetic)
  → P2 spawn-ori-eval dry (GO $)
  → P3 Shop eval #1 (primary)
  → P4 Recommend table → pilot decision
  → P5 Hermes eval (synthetic only)
  → P6 ASA eval (optional)
  → P7 Pin winner env (GO)
  → P8 Bug→eval regressions
  → P9 CI monthly/manual
  → P10 Runbook + START_HERE pointer
```

Параллельно можно: inventory + fixtures shop; CI yaml draft без ключа.

---

## 4. Промпты для Ori (готовые формулировки)

### Shop (первый)

> What is the cheapest model that still correctly handles Stars purchase status, VPN subscription status, and refund/FAQ flows for our Telegram shop assistant — tool calls required, no invented prices — max prompt price Flash-class, optimize $/completed task then latency.

### Hermes

> Best model under Flash-class prompt price for Hermes KB answers: grounded in ALADDIN security KB, no invented family members, no parental-control bypass advice. Synthetic prompts only.

### Regression (шаблон)

> Bug: assistant completed without calling `<tool>` on `<scenario>`. Write a failing eval that asserts the tool is called; keep it in the suite.

---

## 5. GO-точки (пилот)

| GO | Что разрешает | Без GO |
|----|---------------|--------|
| **GO ORI $2** | Первый `spawn-ori-eval` / live model compare | Только docs, inventory, fixtures |
| **GO ORI KEEP** | Сохранить `evals/` в repo (не temp) | Файлы остаются во temp / не коммитим |
| **GO MODEL PIN** | Смена `ASSISTANT_LLM_MODEL` / Hermes model на Brain/MAIN | Только recommendation table |
| **GO CI ORI** | Secrets + schedule workflow | Workflow draft без ключа / `--list` only |

Деплой `.env` на Contabo/MAIN — отдельно по `ask-before-important-ops`.

---

## 6. Артефакты

| Артефакт | Путь |
|----------|------|
| Registry | `.cursor/ORI_EVAL_TASK_REGISTRY.md` |
| Этот план | `docs/PLAN_ORI_EVAL_OPENROUTER_2026-10-05.md` |
| Shop evals (после GO KEEP) | `telegram_stars_shop_bot/evals/**` |
| Hermes/ASA evals (после GO KEEP) | `evals/hermes/**`, `evals/asa/**` (корень backend/security) |
| Report | `eval-report.md` / job summary (не коммитить секреты) |
| Runbook | `docs/ORI_EVAL_RUNBOOK.md` (фаза P10) |

---

## 7. Definition of Done (весь контур)

- [ ] Inventory call-sites зафиксирован в registry
- [ ] ≥1 shop eval suite с отчётом score/latency/$
- [ ] Пилот выбрал: keep Flash / switch / dual-route
- [ ] Prod pin только после GO MODEL PIN + smoke
- [ ] ≥1 regression eval от реального бага (когда появится)
- [ ] CI: list на PR-опционально; live — manual/monthly
- [ ] Runbook + строка в START_HERE

---

## 8. Следующий шаг (сейчас)

1. Закрыть **P0** (этот план + registry) — без денег.  
2. Спросить пилота: **GO ORI $2** на shop dry-run?  
3. Пока нет GO — готовить synthetic fixtures (`ori-03`).
