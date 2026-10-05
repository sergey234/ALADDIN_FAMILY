# Ori Eval × OpenRouter — Task Registry (`ori-*`)

**SSOT** · выбор модели по quality / $/task / latency  
**Для другой ML (делать по нему):** [`docs/ML_SYSTEM_HANDOFF_ORI_EVAL_2026-10-05.md`](../docs/ML_SYSTEM_HANDOFF_ORI_EVAL_2026-10-05.md)  
**Технический черновик:** [`docs/PLAN_ORI_EVAL_OPENROUTER_2026-10-05.md`](../docs/PLAN_ORI_EVAL_OPENROUTER_2026-10-05.md)  
**Rule:** `.cursor/rules/ori-eval-todo-ssot.mdc`  
**Docs:** [Ori Eval](https://openrouter.ai/docs/guides/ori/eval)

## Правила TodoWrite

1. Только `merge: true` — не затирать `af-*` / `ps-*` / `asm-*` / `jam-*` / bot ids.  
2. Закрыл задачу → ✅ здесь → `completed` в Cursor TODO.  
3. Live Ori / смена prod model / CI secret — **только после явного GO** (`ask-before-ops`).  
4. Нет family PII / live child chats / VPN §32 в fixtures.  
5. Bot evals → `telegram_stars_shop_bot/`; **не** в iOS release commit.

## Порядок

```text
ori-00…02 (docs) → ori-03 fixtures → GO ORI $ → ori-04…05 shop
  → ori-08 decision → (GO) ori-09 pin
  → ori-06 Hermes → ori-07 ASA opt → ori-10 regress → ori-11 CI → ori-12 docs
```

---

## Фаза P0 — План и инвентарь

| ID | Задача | GO? | Статус |
|----|--------|-----|--------|
| `ori-00-plan` | План + этот registry + todo-ssot rule | — | ✅ 2026-10-05 |
| `ori-01-gates` | GATES G1–G8 в плане; бюджет default $2 | — | ✅ 2026-10-05 |
| `ori-02-inventory` | Таблица call-sites: env keys, default model, failover, host | — | ⬜ |

### Inventory checklist (`ori-02`)

| Surface | Env / code | Default | Host |
|---------|------------|---------|------|
| Hermes | `OPENROUTER_*`, Hermes model | `deepseek/deepseek-v4-flash` | 🇷🇺 MAIN (`…180`) |
| OpenRouter direct fallback | `OPENROUTER_DIRECT_MODEL` | `deepseek/deepseek-v4-flash` | MAIN |
| Shop assistant | `ASSISTANT_LLM_MODEL` + `ASSISTANT_LLM_FALLBACK_MODELS` | Flash → chat → free | 🇩🇪 Brain (`…150`) |
| ASA | `ASA_LLM_MODEL` / `OPENROUTER_MODEL` | `deepseek/deepseek-chat` + free chain | MAIN (+ relay) |
| AI PM judge | `OPENROUTER_MODEL` / live flag | `deepseek/deepseek-chat` | local/CI |

---

## Фаза P1 — Fixtures (без денег)

| ID | Задача | GO? | Статус |
|----|--------|-----|--------|
| `ori-03-fixtures` | Synthetic shop cases: Stars status, VPN status, refund/FAQ; mustMention + expected tools; **no PII** | — | ⬜ |

---

## Фаза P2 — Первый live Ori (shop)

| ID | Задача | GO? | Статус |
|----|--------|-----|--------|
| `ori-04-spawn-dry` | `spawn-ori-eval` во **temp**; login; budget ≤ $2 | **GO ORI $2** | ⬜ |
| `ori-05-shop-eval` | Model compare shop: score / p50 / $/task; Flash-class `maxPromptPrice` | после 04 | ⬜ |
| `ori-08-recommend` | Таблица кандидатов + рекомендация keep/switch/dual → решение пилота | после 05 | ⬜ |

---

## Фаза P3 — Pin и вторичные evals

| ID | Задача | GO? | Статус |
|----|--------|-----|--------|
| `ori-09-env-pin` | Pin winner в env (Brain/MAIN) + smoke; без auto | **GO MODEL PIN** | ⬜ |
| `ori-06-hermes-eval` | Hermes KB synthetic; Pro вне кандидатов без отдельного credit GO | GO $ (можно тот же) | ⬜ |
| `ori-07-asa-eval` | ASA classify/tool asserts (optional, после shop) | — | ⬜ |

---

## Фаза P4 — Регрессии и CI

| ID | Задача | GO? | Статус |
|----|--------|-----|--------|
| `ori-10-regress` | Bug → failing eval → fix → green; оставить в suite | — | ⬜ |
| `ori-11-ci` | GH Actions: `workflow_dispatch` + monthly; secret; не unit-job | **GO CI ORI** | ⬜ |
| `ori-12-docs` | `docs/ORI_EVAL_RUNBOOK.md` + pointer в START_HERE / AGENTS | — | ⬜ |

---

## GO log

| Дата | GO | Решение |
|------|-----|---------|
| — | — | ожидает пилота |

---

## Запреты

- Auto-merge model PR без пилота  
- `openrouter/auto` на parental/family surfaces  
- Live family logs в Ori  
- Коммит bot evals внутрь iOS `feat(build N)`  
- Live Ori в каждом PR (дорого)  
